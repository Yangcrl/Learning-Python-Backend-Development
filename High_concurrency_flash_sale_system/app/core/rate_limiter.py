"""
基于 Redis 的滑动窗口限流实现
"""

import time
import redis

class RateLimiter:
    def __init__(self, redis_client, key_prefix, limit, window):
        """
        初始化限流计数器
        :param redis_client: Redis 客户端
        :param key_prefix: 键前缀
        :param limit: 时间窗口内的最大请求数
        :param window: 时间窗口大小（秒）
        """
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.limit = limit
        self.window = window
    
    def is_allowed(self, user_id):
        """
        检查是否允许请求
        :param user_id: 用户ID
        :return: True 表示允许，False 表示拒绝
        """
        key = f"{self.key_prefix}:{user_id}"
        current_time = time.time()
        
        try:
            # 移除时间窗口外的请求
            self.redis_client.zremrangebyscore(key, 0, current_time - self.window)
            
            # 获取当前时间窗口内的请求数
            count = self.redis_client.zcard(key)
            
            if count < self.limit:
                # 添加当前请求的时间戳
                # 使用字典格式，适用于 Redis 5.1.0+
                self.redis_client.zadd(key, {str(current_time): current_time})
                # 设置键的过期时间，避免内存泄漏
                self.redis_client.expire(key, self.window)
                return True
            else:
                return False
        except Exception as e:
            print(f"限流检查失败: {str(e)}")
            # 出错时默认允许请求，避免影响正常业务
            return True
