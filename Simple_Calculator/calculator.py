# 目标：做一个简单的计算器模型。功能包括：加减乘除、括号、幂、小数、负数
# 如后续有时间，所添加功能在此注释下面补充
def calculate(expression):
    # 支持的合法字符
    legal_chars = '0123456789+-*/.**().'

    # 过滤非法字符
    expression = ''.join([i for i in expression if i in legal_chars])

    # 校验空输入
    if not expression:
        return '错误：表达式不能为空！'

    # 功能部分
    try:
        # 计算  eval(): 执行字符串表达式
        result = eval(expression)

        # 优化结果显示：整数型浮点数转为纯整数；小数保留6位，避免超长尾数
        # isinstance():判断对象类型  is_integer():判断是否为整数
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        else:
            result = round(result, 6)

        return f"计算结果：{result}"
    except ZeroDivisionError:
        return '错误：除数不能为零！'
    except SyntaxError:
        return '错误：表达式格式错误！'
    except:
        return f'错误：无法计算该表达式，请检查格式！'

def main():
    """计算机主函数，进行交互"""
    print("===== Python 全能计算器 =====")

    while True:
        # 获取用户输入
        user_input = input("请输入表达式：").strip()

        # 退出条件  lower(): 将字符串转换为小写
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("计算机已退出，感谢使用！")
            break

        # 计算并输出结果
        result = calculate(user_input)
        print(result)


# 启动计算器
if __name__ == '__main__':
    main()




