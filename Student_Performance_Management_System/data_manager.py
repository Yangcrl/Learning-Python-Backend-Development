"""
职责：1.定义学生数据结构  2.实现增删改查核心功能 3.整合数据持久化
所有数据操作后自动保存到文件，程序启动时从文件加载
"""

# 导入工具函数
from utils import is_valid_id, is_valid_score, calculate_total_score, calculate_average_score
from persistence import save_data_to_file, load_data_from_file

# 定义核心数据结构
# 全局内存容器：key=学号（6位字符串），value=学生信息字典
# 结构示例：
# students = {
#     "202401": {
#         "name": "张三",
#         "scores": {"数学": 95.0, "语文": 88.0},  # 成绩存数字
#         "total": 183.0,  # 总分（自动计算）
#         "average": 91.5  # 平均分（自动计算）
#     }
# }
# 启动时从文件加载数据
students = {}

# 初始化：程序启动时加载数据
def init_data():
    """初始化数据：从文件加载学生数据"""
    success, data = load_data_from_file()
    if success:
        global students
        students = data
        print(f"成功加载{len(students)}条学生数据")
    else:
        print(f"加载失败：{data}")

# 实现核心功能（增删改查）
# 添加学生信息
# 新增自动保存（3.18）
def add_student(student_id, name, scores):
    """
    添加学生（接收ui层传入的用户输入数据）
    :param student_id: 用户输入的学号（字符串）
    :param name: 用户输入的姓名（字符串）
    :param scores: 用户输入的成绩字典（{科目: 成绩字符串}）
    :return: (是否成功, 提示信息)
    """
    # 验证学号是否正确
    if not is_valid_id(student_id):
        return False, "学号格式错误，请输入6位数字"

    # 验证学号是否重复
    if student_id in students:
        return False, "学号已存在"

    # 新增：姓名非空校验
    if not name.strip():
        return False, "姓名不能为空"

    # 验证成绩合法性
    for subject, score in scores.items():
        if not is_valid_score(score):
            return False, f"{subject}科目的成绩{score}不合法！"

    # 构造符合数据结构的学生信息（成绩转数字）
    score_dict = {sub: float(sc) for sub, sc in scores.items()}
    student_info = {
        "name": name,
        "scores": score_dict,
        "total": calculate_total_score(score_dict),
        "average": calculate_average_score(score_dict)
    }

    # 存入内存容器
    students[student_id] = student_info

    # 新增：保存到文件
    save_success, save_msg = save_data_to_file(students)
    if not save_success:
        return False, f"学生{name}添加成功，但数据保存失败：{save_msg}"
    return True, f"学生{name}(学号{student_id})添加成功"

# 删除学生信息
# 新增自动保存（3.18）
def del_student(student_id):
    """
    删除学生（接收ui层传入的学号）
    :param student_id: 用户输入的学号
    :return: 是否成功，提示信息
    """
    # 判断学号是否存在
    if student_id not in students:
        return False, f"学号{student_id}不存在，无法删除"

    # 删除学生信息
    del students[student_id]

    # 新增：保存到文件
    save_success, save_msg = save_data_to_file(students)
    if not save_success:
        return False, f"学生{student_id}删除成功，但数据保存失败：{save_msg}"
    return True, f"学生{student_id}删除成功"

# 修改学生成绩
# 新增自动保存（3.18）
def modify_student_score(student_id, subject, new_score_s):
    """
    修改学生成绩（接收ui层传入的修改数据）
    :param student_id: 用户输入的学号
    :param subject: 用户输入的科目
    :param new_score_s: 用户输入的新成绩
    :return: 是否成功，提示信息
    """
    # 判断学号是否存在
    if student_id not in students:
        return False, f"学号{student_id}不存在，无法修改"

    # 验证新成绩合法性
    if not is_valid_score(new_score_s):
        return False, f"新成绩不合法"

    # 检查科目是否存在
    if subject not in students[student_id]["scores"]:
        return False, f"科目{subject}不存在"

    # 修改成绩并更新总分、平均分
    new_score = float(new_score_s)
    students[student_id]["scores"][subject] = new_score
    students[student_id]["total"] = calculate_total_score(students[student_id]["scores"])
    students[student_id]["average"] = calculate_average_score(students[student_id]["scores"])

    # 新增：保存到文件
    save_success, save_msg = save_data_to_file(students)
    if not save_success:
        return False, f"学生{student_id}修改成功，但数据保存失败：{save_msg}"
    return True, f"学生{student_id}"


# 查询学生成绩
def query_student(keyword):
    """
    查询学生信息（支持学号精确匹配、姓名模糊匹配）
    :param keyword: 查询关键词（学号/姓名，字符串）
    :return: list- 匹配的学生信息列表（空列表表示无匹配结果）
                列表中每个元素为字典，结构：
                {
                    'student_id': 学号,
                    'name': 姓名,
                    'scores': 成绩字典,
                    'total': 总分,
                    'average': 平均分
                }
    """
    # 初始化查询结果列表
    query_results = []

    # 遍历所有学生数据，逐一匹配
    for sid, info in students.items():
        # 匹配规则：学号完全一致 or 姓名包含关键词（不区分大小写）
        if sid == keyword or keyword.lower() in info['name'].lower():
            # 构造统一格式的结果，方便ui层展示
            query_results.append({
                'student_id': sid,
                'name': info['name'],
                'scores': info['scores'],
                'total': info['total'],
                'average': info['average']
            })
    return query_results

# 获取所有学生信息
def get_all_students():
    """
    获取所有学生信息（按学号排序）
    """
    sorted_students = sorted(students.items(), key=lambda x: x[0]) # key指定排序依据为学号
    results = []
    for sid, info in sorted_students:
        results.append({
            "student_id": sid,
            "name": info['name'],
            "scores": info['scores'],
            "total": info['total'],
            "average": info['average']
        })
    return results