"""
异步Redis客户端
使用aioredis库实现异步Redis操作
"""

import aioredis
import os
from typing import Optional, AsyncGenerator
import json

# 尝试导入环境变量加载工具

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found, using default values")

"""redis配置"""
# redis 服务地址
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
# redis 端口
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# redis 密码
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "123456")
# reids 数据库编号，默认0
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# 全局Redis连接池
redis_pool = None

async def get_redis_pool() -> aioredis.Redis:
    """
    获取Redis连接池
    """
    global redis_pool
    if redis_pool is None:
        redis_pool = await aioredis.create_redis_pool(
            address=(REDIS_HOST, REDIS_PORT),
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            encoding="utf-8"
        )
    return redis_pool

async def get_redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    """
    获取Redis客户端
    """
    pool = await get_redis_pool()
    try:
        yield pool
    except Exception as e:
        print(f"Redis 连接异常：{str(e)}")
        raise e

"""异步Redis缓存工具类"""
class AsyncRedisCacheUtil:
    """
    封装秒杀项目常用的缓存操作，自动处理JSON序列化/反序列化
    """

    @staticmethod
    async def set_cache(
            client: aioredis.Redis,
            key: str,
            value: any,
            expire: Optional[int] = 600,  # 默认缓存10分钟
            nx: bool = False              # nx = True 表示key不存在时才设置缓存
    ) -> bool:
        """
        写入缓存
        """
        try:
            # 将Python 对象转为JSON 字符串
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            # 写入Redis
            if nx:
                result = await client.set(key, json_value, ex=expire, nx=True)
            else:
                result = await client.set(key, json_value, ex=expire)
            return result is not None
        except Exception as e:
            print(f"Redis 写入缓存异常：key={key}, 错误={str(e)}")
            return False

    @staticmethod
    async def get_cache(
            client: aioredis.Redis,
            key: str
    ) -> Optional[any]:
        """
        获取缓存
        """
        try:
            json_value = await client.get(key)
            # 如果缓存值不存在，返回None
            if json_value is None:
                return None
            # 将JSON字符串转为Python对象
            return json.loads(json_value)
        except Exception as e:
            print(f"Redis 读取缓存异常：key={key}, 错误={str(e)}")
            return None

    @staticmethod
    async def delete_cache(
            client: aioredis.Redis,
            key: str
    ) -> bool:
        """
        删除缓存
        """
        try:
            await client.delete(key)
            return True
        except Exception as e:
            print(f"Redis 删除缓存异常：key={key}, 错误={str(e)}")
            return False

    @staticmethod
    async def is_exist(
            client: aioredis.Redis,
            key: str
    ) -> bool:
        """
        检查key 是否存在
        """
        try:
            return await client.exists(key) > 0
        except Exception as e:
            print(f"Redis 检查key异常：key={key}, 错误={str(e)}")
            return False

    @staticmethod
    async def hset(
            client: aioredis.Redis,
            key: str,
            field: str,
            value: any
    ) -> bool:
        """
        设置哈希表字段
        """
        try:
            await client.hset(key, field, value)
            return True
        except Exception as e:
            print(f"Redis hset异常：key={key}, field={field}, 错误={str(e)}")
            return False

    @staticmethod
    async def hget(
            client: aioredis.Redis,
            key: str,
            field: str
    ) -> Optional[str]:
        """
        获取哈希表字段
        """
        try:
            return await client.hget(key, field)
        except Exception as e:
            print(f"Redis hget异常：key={key}, field={field}, 错误={str(e)}")
            return None

    @staticmethod
    async def hgetall(
            client: aioredis.Redis,
            key: str
    ) -> Optional[dict]:
        """
        获取哈希表所有字段
        """
        try:
            return await client.hgetall(key)
        except Exception as e:
            print(f"Redis hgetall异常：key={key}, 错误={str(e)}")
            return None
