import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

url = "http://127.0.0.1:8000/api/products/1"

print("准备场景2：有缓存压测")
print("=" * 50)
print("1. 先调用API接口，让缓存写入Redis")
print(f"调用URL: {url}")

# 调用API接口，写入缓存
try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ API调用成功!")
        print("✓ 缓存已写入Redis")
    else:
        print("\n✗ API调用失败")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"\n✗ 请求失败: {str(e)}")

print("\n2. 验证Redis缓存是否存在")
print("=" * 50)
