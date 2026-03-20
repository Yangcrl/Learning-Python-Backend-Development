"""
职责：数据持久化（json文件读写）
为data_manager提供数据保存到文件、从文件加载的能力
"""

import json
import os

# 定义数据存储文件路径
"""
__file__ 是当前脚本的完整路径，os.path.dirname() 提取脚本所在目录
os.path.join() 按系统规则拼接路径，保证跨平台兼容性
整体作用是：精准定位到和当前脚本同目录的 students.json 文件，避免路径错误
"""
DATA_FILE = os.path.join(os.path.dirname(__file__), "students.json")

def save_data_to_file(data):
    """
    将数据保存到文件中
    :param data: 要保存的学生字典（同data_manager中的students结构）
    :return: 是否成功，提示信息
    """
    try:
        # 确保json序列化时能处理浮点数，格式化输出
        """
        核心功能：把 Python 数据（学生信息）保存为 UTF-8 编码的 JSON 文件，保证中文正常显示且格式美观
        关键特性：with 自动管理文件、ensure_ascii=False 支持中文、indent=4 格式化输出
        """
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True, "学生数据已保存成功"
    except PermissionError:
        return False, "权限不足，无法写入文件"
    except Exception as e:
        return False, f"保存数据时发生错误：{e}"

def load_data_from_file():
    """
    从文件中加载数据
    :return: 学生信息字典
    """
    # 文件不存在时，创建一个空字典并返回
    if not os.path.exists(DATA_FILE):
        return True, {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data
    except PermissionError:
        return False, "权限不足，无法读取文件"
    except Exception as e:
        return False, f"加载数据时发生错误：{e}"