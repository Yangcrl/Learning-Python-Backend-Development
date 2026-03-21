"""
装饰器模块
职责：提供通用的函数装饰器（如计时器）
"""

import time
import functools

def timer_decorator(func):
    """
    计时器装饰器：测量函数执行时间并打印
    :param func: 被装饰的函数
    :return: 包装后的函数
    """
    @functools.wraps(func) # 保留被装饰函数的元信息
    def wrapper(*args, **kwargs):
        # 记录开始时间（perf_counter 精度更高）
        start_time = time.perf_counter()

        # 执行原函数并获取返回值
        ret = func(*args, **kwargs)

        # 记录结束时间并计算耗时
        end_time = time.perf_counter()
        cost_time = end_time - start_time

        # 格式化输出：函数名 + 执行时间（根据时长选择单位）
        if cost_time < 1: # 毫秒
            print(f"{func.__name__} 耗时 {cost_time * 1000:.2f} ms")
        else: # 秒
            print(f"{func.__name__} 耗时 {cost_time:.2f} s")

        # 返回原函数的返回值
        return ret
    return wrapper