import requests

url = "http://127.0.0.1:8000/api/products/1"

print(f"测试API接口: {url}")
print("=" * 50)

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("\n✓ API调用成功!")
        print("✓ 数据库中存在ID为1的商品数据")
    else:
        print("\n✗ API调用失败")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"\n✗ 请求失败: {str(e)}")
