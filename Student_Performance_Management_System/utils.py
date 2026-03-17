"""
工具函数模块
职责：通用工具函数：数据验证、成绩计算
为data_manager层提供支持，不直接处理用户交互
"""

# 数据验证
# 验证学号，确保学号是六位数字
def is_valid_id(student_id):
    """
    验证学号：必须是6位纯数字字符串
    :param student_id: 学生学号
    """
    if isinstance(student_id, str) and len(student_id) == 6 and student_id.isdigit():
        return True
    return False

# 验证成绩的合法性
def is_valid_score(score_str):
    """
    验证成绩：必须是0-100的数字（支持整数/小数）
    :param score_str: 成绩（字符）
    """
    try:
        score = float(score_str)
        return 0 <= score <=100
    except ValueError:
        # 成绩（字符）转换成数字失败（非数字），则不合法
        return False

# 计算总分
def calculate_total_score(scores):
    """
    计算总分（接收数字类型的成绩字典）
    :param scores: 数字类型的成绩字典
    :return: 所给成绩字典的总分
    """
    return sum(scores.values())

# 计算平均分
def calculate_average_score(scores):
    """
    计算平均分（保留2位小数）
    """
    if not scores: # 避免除以0
        return 0.0
    total = calculate_total_score(scores)
    return round(total / len(scores), 2)
