"""
职责：程序入口（启动系统，菜单循环）
唯一的启动文件，整合ui层的所有功能
"""

from ui import show_main_menu,handle_add, handle_query, handle_modify, handle_delete, handle_show_all

# 主函数：系统启动入口
def main():
    print("欢迎使用学生成绩管理系统！（内存版）")

    # 菜单循环
    while True:
        # 显示菜单
        show_main_menu()
        try:
            # 接收用户的操作选择
            choice = int(input("请输入您的选择操作（0-5）："))
            # 菜单选择逻辑
            if choice == 1:
                handle_add()
            elif choice == 2:
                handle_delete()
            elif choice == 3:
                handle_modify()
            elif choice == 4:
                handle_query()
            elif choice == 5:
                handle_show_all()
            elif choice == 0:
                print("感谢使用学生成绩管理系统！")
                break
            else:
                print("无效的选择，请重新输入！")
        except KeyboardInterrupt:
            print("程序被强制中断，即将退出...")
            break
        except Exception as e:
            print("程序发生错误：", e)

# 启动系统
if __name__ == '__main__':
    main()