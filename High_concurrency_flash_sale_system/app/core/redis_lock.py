"""
Redis 分布式锁实现
"""

import redis
import uuid

class RedisLock:
    def __init__(self, redis_client, key, expire=10):
        """
        初始化分布式锁
        :param redis_client: Redis 客户端
        :param key: 锁的键名
        :param expire: 锁的过期时间（秒）
        """
        self.redis_client = redis_client
        self.key = key
        self.expire = expire
        self.identifier = str(uuid.uuid4())
    
    def acquire(self):
        """
        获取锁
        :return: True 表示获取成功，False 表示获取失败
        """
        # 使用 setnx 命令，设置键值对，同时设置过期时间
        # nx: 只有当键不存在时才设置
        # ex: 设置过期时间
        result = self.redis_client.set(
            self.key, 
            self.identifier, 
            nx=True, 
            ex=self.expire
        )
        return result is True
    
    def release(self):
        """
        释放锁
        使用 Lua 脚本确保原子性
        """
        # Lua 脚本，确保只有锁的持有者才能释放锁
        lua_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        # 替换脚本中的 ARGV[1]
        lua_script = lua_script.replace('ARGV[1]', f'"{self.identifier}"')
        # 执行 Lua 脚本
        result = self.redis_client.eval(lua_script, 1, self.key)
        return result == 1
