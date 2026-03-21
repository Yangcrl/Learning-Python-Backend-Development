"""
职责：用户交互界面：接收输入，展示结果
所有输入逻辑都在这里，调用data_manager的功能函数完成业务
"""
# 导入data_manager的功能函数
from data_manager import add_student, del_student, modify_student_score, get_all_students, query_student

# ===交互菜单展示===
def show_main_menu():
    """显示主菜单（用户操作入口）"""
    print("\n" + "="*30)
    print("学生成绩管理系统（内存版）+（文件持久化）")
    print("="*30)
    print("    请选择要执行的操作（0-5）")
    print("    1. 添加学生成绩")
    print("    2. 删除学生成绩")
    print("    3. 修改学生成绩")
    print("    4. 查询学生成绩")
    print("    5. 列出所有学生成绩")
    print("    0. 退出系统")
    print("="*30)

# ===输入处理（用户输入的核心逻辑）===
def input_student_basic_info():
    """接收用户输入：学号，姓名，多门科目成绩"""
    print('\n---- 添加学生 ----')

    # 输入学号
    # 优化：循环直到输入合法格式（3.18）
    while True:
        student_id = input("请输入学生学号(6为数字，如202603)：").strip()
        if student_id.isdigit() and len(student_id) == 6:
            break
        print("学号格式错误，请重新输入")

    # 输入姓名
    # 优化：循环直到非空（3.18）
    while True:
        name = input('请输入学生姓名：').strip()
        if name:
            break
        print("姓名不能为空，请重新输入！")

    # 输入多门科目成绩（循环输入，直到输入q结束）
    scores = {}
    print("\n请输入科目成绩(输入'q'结束)：")
    while True:
        subject = input('科目名称：').strip()
        # 输入q则退出循环
        if subject.lower() == 'q':
            break
        # 空科目名提示
        if not subject:
            print("科目名称不能为空，请重新输入！")
            continue

        # 输入该科成绩
        # 优化：成功输入校验
        while True:
            score = input(f"{subject}成绩：").strip()
            # 判断是否为数字
            try:
                float(score)
                break
            except ValueError:
                print("成绩格式错误，请重新输入")
        scores[subject] = score

    return student_id, name, scores

def input_query_keyword():
    """
    接收用户输入：查询关键词（学号/姓名）
    :return: 关键词
    """
    print('\n---- 查询学生 ----')
    # 优化（3.18）
    while True:
        keyword = input("请输入学号或姓名：").strip()
        if keyword:
            break
        print("关键词不能为空，请重新输入！")
    return keyword

def input_modify_info():
    """接收用户输入：修改成绩的学号、科目、成绩"""
    print('\n---- 修改成绩 ----')
    # 优化判断（3.18）
    while True:
        student_id = input("请输入要修改的学生学号：").strip()
        if student_id:
            break
        print("学号不能为空，请重新输入！")
    while True:
        subject = input("请输入要修改的科目名称：").strip()
        if subject:
            break
        print("科目名称不能为空，请重新输入！")
    while True:
        new_score = input("请输入新的成绩：").strip()
        try:
            float(new_score)
            break
        except ValueError:
            print("成绩格式错误，请重新输入！")
    return student_id, subject, new_score

def input_delete_id():
    """接收用户输入：要删除的学生学号"""
    print('\n---- 删除学生 ----')
    # 优化判断（3.18）
    while True:
        student_id = input("请输入要删除的学生学号：").strip()
        if len(student_id) == 6 and student_id.isdigit():
            break
        print("学号格式错误，请重新输入！")
    return student_id

# ===结果展示===
def print_student_list(student_list):
    """格式化展示查询结果"""
    if not student_list:
        print("未找到匹配的学生信息！")
        return # 函数结束

    print("---学生成绩信息---")
    for idx, student in enumerate(student_list):
        print(f"学号：{student['student_id']}", end='  ')
        print(f"姓名：{student['name']}")
        print(f"成绩：")
        for sub, sc in student['scores'].items():
            print(f"-{sub}: {sc}")
        print(f"总分：{student['total']} | 平均分：{student['average']}")
    print('-'*20)


# ===业务处理===
# 处理查询的完整流程
def handle_query():
    """输入->查询->展示"""
    keyword = input_query_keyword()
    results = query_student(keyword)
    print_student_list( results)

# 处理添加学生的完整流程
def handle_add():
    """输入->添加->结果展示"""
    # 获取用户输入
    student_id, name, scores = input_student_basic_info()
    # 空成绩校验
    if not scores:
        print("添加失败！至少要输入一门科目成绩！")
        return
    # 调用核心功能
    success, msg = add_student(student_id, name, scores)
    # 展示结果
    print(msg)

# 处理修改成绩的完整流程
def handle_modify():
    """输入->修改->结果展示"""
    # 获取用户输入
    student_id, subject, new_score = input_modify_info()
    # 调用核心功能
    success, msg = modify_student_score(student_id, subject, new_score)
    # 展示结果
    print(msg)

# 处理删除学生的完整流程（含二次确认）
# 优化判断（3.18）
def handle_delete():
    """输入->二次确认->删除->结果展示"""
    # 获取用户输入
    student_id = input_delete_id()
    # 二次确认
    while True:
        confirm = input(f"确定要删除学号为{student_id}的学生吗？(y/n)").strip()
        if confirm in ['y', 'n']:
            break
        print("输入错误，仅支持输入y（确认）/n（取消）")
    if confirm == 'n':
        print("取消删除")
        return
    success, msg = del_student(student_id)
    print(msg)

# 处理列出所有学生的完整流程
def handle_show_all():
    """展示所有学生信息"""
    # 调用核心功能
    all_students = get_all_students()
    # 展示结果
    if not all_students:
        print("暂无数据")
        return
    print_student_list(all_students)