import requests
import time

# 测试缓存穿透防护
print("测试缓存穿透防护...")
print("=" * 60)

# 测试1：访问存在的商品ID（应该成功）
print("测试1：访问存在的商品ID")
url = "http://127.0.0.1:8001/api/products/1"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 200:
        print("访问成功，商品存在")
    else:
        print("访问失败")
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n" + "=" * 60)

# 测试2：访问不存在的商品ID（应该被布隆过滤器拦截）
print("测试2：访问不存在的商品ID")
url = "http://127.0.0.1:8001/api/products/999999"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    if response.status_code == 404:
        print("访问被拦截，布隆过滤器工作正常")
    else:
        print("访问未被拦截，布隆过滤器可能未工作")
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n" + "=" * 60)

# 测试3：并发测试，模拟缓存穿透攻击
print("测试3：并发测试，模拟缓存穿透攻击")
def test_request(product_id):
    url = f"http://127.0.0.1:8001/api/products/{product_id}"
    try:
        response = requests.get(url, timeout=1)
        return response.status_code
    except:
        return 0

# 模拟100次请求不存在的商品ID
import threading
results = []
threads = []

start_time = time.time()
for i in range(100):
    # 生成随机的不存在的商品ID
    product_id = 1000000 + i
    t = threading.Thread(target=lambda: results.append(test_request(product_id)))
    t.start()
    threads.append(t)

# 等待所有线程完成
for t in threads:
    t.join()

end_time = time.time()

# 统计结果
status_404 = results.count(404)
status_other = len(results) - status_404

print(f"并发请求数: 100")
print(f"404 响应数: {status_404}")
print(f"其他响应数: {status_other}")
print(f"执行时间: {end_time - start_time:.2f} 秒")

if status_404 == 100:
    print("所有请求都被布隆过滤器拦截，缓存穿透防护成功")
else:
    print("部分请求未被拦截，缓存穿透防护可能存在问题")

print("\n测试完成！")
