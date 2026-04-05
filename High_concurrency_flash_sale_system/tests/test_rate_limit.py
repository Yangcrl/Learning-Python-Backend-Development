"""
测试限流功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time

# 测试配置
url = "http://127.0.0.1:8000/seckill/1"
user_id = "test_user"

# 测试函数
def test_rate_limit():
    print("测试限流功能...")
    print("=" * 60)
    print(f"测试URL: {url}")
    print(f"用户ID: {user_id}")
    print("\n开始发送高频请求...")
    
    # 发送15次请求，应该会被限流
    for i in range(15):
        headers = {"X-User-ID": user_id}
        try:
            print(f"发送请求 {i+1}...")
            response = requests.post(url, headers=headers, timeout=3)
            print(f"请求 {i+1}: 状态码={response.status_code}")
            if response.status_code == 429:
                print(f"  被限流了！响应内容: {response.text}")
                break
            elif response.status_code == 200:
                data = response.json()
                print(f"  秒杀成功！剩余库存: {data['remaining_stock']}")
            else:
                print(f"  其他错误: {response.text}")
        except Exception as e:
            print(f"  请求失败: {str(e)}")
        # 短暂延迟，避免网络问题
        time.sleep(0.2)
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_rate_limit()
