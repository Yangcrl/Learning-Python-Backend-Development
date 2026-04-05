"""
Redis 客户端配置
"""

import redis
from app.core.config import settings
from typing import Optional

# 创建Redis连接池
pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
    decode_responses=True  # 自动解码
)

# 依赖注入：获取Redis客户端
def get_redis_client():
    """
    获取Redis客户端
    """
    redis_client = redis.Redis(connection_pool=pool)
    try:
        yield redis_client
    finally:
        redis_client.close()
