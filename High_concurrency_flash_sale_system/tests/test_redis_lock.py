"""
测试 Redis 分布式锁的并发性能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis
import threading
import time
from app.core.redis_client import pool
from app.core.redis_lock import RedisLock

# 测试配置
lock_key = "test:lock"
test_count = 100
thread_count = 10

# 共享资源
shared_resource = 0

# 线程锁
print_lock = threading.Lock()

def test_thread():
    """测试线程"""
    global shared_resource
    redis_client = redis.Redis(connection_pool=pool, decode_responses=True)
    lock = RedisLock(redis_client, lock_key, expire=5)
    
    for _ in range(test_count):
        # 获取锁
        while not lock.acquire():
            time.sleep(0.01)
        
        # 访问共享资源
        shared_resource += 1
        with print_lock:
            print(f"Thread {threading.current_thread().name}: {shared_resource}")
        
        # 释放锁
        lock.release()

# 开始测试
print(f"开始测试，线程数: {thread_count}，每个线程操作次数: {test_count}")
print("=" * 60)

start_time = time.time()

threads = []
for i in range(thread_count):
    t = threading.Thread(target=test_thread, name=f"Thread-{i}")
    t.start()
    threads.append(t)

# 等待所有线程完成
for t in threads:
    t.join()

end_time = time.time()

print("=" * 60)
print(f"测试完成，耗时: {end_time - start_time:.2f} 秒")
print(f"预期结果: {thread_count * test_count}")
print(f"实际结果: {shared_resource}")

if shared_resource == thread_count * test_count:
    print("✓ 测试成功，没有出现并发问题")
else:
    print("✗ 测试失败，出现并发问题")
