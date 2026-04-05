"""
限流中间件
"""

from fastapi import Request, HTTPException
import redis
from app.core.redis_client import pool
from app.core.rate_limiter import RateLimiter

async def rate_limit_middleware(request: Request, call_next):
    """
    限流中间件
    限制同一用户每秒最多 10 次请求
    """
    # 从请求中获取用户ID（这里简化处理，实际应该从认证信息中获取）
    user_id = request.headers.get("X-User-ID", "anonymous")
    
    # 获取 Redis 客户端
    redis_client = redis.Redis(connection_pool=pool, decode_responses=True)
    
    # 初始化限流器
    rate_limiter = RateLimiter(
        redis_client=redis_client,
        key_prefix="rate:limit",
        limit=10,  # 每秒最多 10 次请求
        window=1   # 1秒窗口
    )
    
    # 检查是否允许请求
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后重试")
    
    # 继续处理请求
    response = await call_next(request)
    return response
