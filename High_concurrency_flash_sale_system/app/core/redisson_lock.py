"""
Redisson 分布式锁实现
"""

import redisson

class RedissonLock:
    def __init__(self, redis_url, lock_name):
        """
        初始化 Redisson 客户端和锁
        :param redis_url: Redis 连接 URL
        :param lock_name: 锁的名称
        """
        # 创建 Redisson 客户端
        self.client = redisson.Redisson(
            config={
                'singleServerConfig': {
                    'address': redis_url
                }
            }
        )
        # 获取锁
        self.lock = self.client.getLock(lock_name)
    
    def acquire(self, wait_time=10, lease_time=30):
        """
        获取锁
        :param wait_time: 等待时间（秒）
        :param lease_time: 锁的持有时间（秒）
        :return: True 表示获取成功，False 表示获取失败
        """
        return self.lock.tryLock(wait_time, lease_time)
    
    def release(self):
        """
        释放锁
        """
        if self.lock.isHeldByCurrentThread():
            self.lock.unlock()
    
    def close(self):
        """
        关闭 Redisson 客户端
        """
        self.client.shutdown()
