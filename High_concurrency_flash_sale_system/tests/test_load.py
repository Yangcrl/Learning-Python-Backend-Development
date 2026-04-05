import requests
import time
import threading

# 测试配置
url = "http://127.0.0.1:8000/api/products/1"
duration = 30  # 压测持续时间（秒）
threads = 12   # 线程数
connections = 400  # 总连接数

# 统计数据
total_requests = 0
successful_requests = 0
total_response_time = 0
start_time = 0

# 线程锁
lock = threading.Lock()

# 单个线程的测试函数
def test_thread():
    global total_requests, successful_requests, total_response_time
    end_time = start_time + duration
    while time.time() < end_time:
        try:
            start = time.time()
            response = requests.get(url)
            end = time.time()
            with lock:
                total_requests += 1
                if response.status_code == 200:
                    successful_requests += 1
                    total_response_time += (end - start)
        except Exception as e:
            with lock:
                total_requests += 1

# 开始压测
print("开始压测...")
start_time = time.time()

# 创建并启动线程
thread_list = []
for i in range(threads):
    t = threading.Thread(target=test_thread)
    t.daemon = True
    t.start()
    thread_list.append(t)

# 等待压测结束
time.sleep(duration)

# 计算结果
end_time = time.time()
elapsed_time = end_time - start_time
qps = total_requests / elapsed_time if elapsed_time > 0 else 0
avg_response_time = total_response_time / successful_requests if successful_requests > 0 else 0
success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0

# 输出结果
print("\n压测结果：")
print(f"总请求数: {total_requests}")
print(f"成功请求数: {successful_requests}")
print(f"成功率: {success_rate:.2f}%")
print(f"QPS: {qps:.2f}")
print(f"平均响应时间: {avg_response_time:.4f} 秒")
print(f"压测持续时间: {elapsed_time:.2f} 秒")
