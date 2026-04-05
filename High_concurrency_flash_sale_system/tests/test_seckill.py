"""
测试秒杀接口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# 测试秒杀接口
print("测试秒杀接口...")
print("=" * 60)

# 测试1：正常秒杀
try:
    url = "http://127.0.0.1:8000/seckill/1"
    response = requests.post(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    if response.status_code == 200:
        print("秒杀成功！")
    else:
        print("秒杀失败！")
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n" + "=" * 60)

# 测试2：检查剩余库存
import redis
from app.core.redis_client import pool

redis_client = redis.Redis(connection_pool=pool, decode_responses=True)
try:
    stock_key = "seckill:stock:1"
    remaining_stock = redis_client.hget(stock_key, "stock")
    print(f"当前剩余库存: {remaining_stock}")
finally:
    redis_client.close()

print("\n测试完成！")
