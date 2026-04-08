"""
秒杀接口路由文件
对外提供秒杀相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from redis import Redis
from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.core.redis_lock import RedisLock
from app.core.rabbitmq import rabbitmq_manager
from app.models import SeckillActivity
import time
import uuid

# 创建路由
router = APIRouter(
    prefix="/seckill",  # 所有接口都以这个开头
    tags=["秒杀管理"]         # 接口文档里分组显示
)

# 读取Lua脚本
def load_lua_script():
    with open("lua/stock.lua", "r", encoding="utf-8") as f:
        return f.read()

# 秒杀接口
@router.post("/{activity_id}", summary="秒杀商品")
def seckill(
    activity_id: int,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    秒杀商品接口
    1. 检查秒杀活动是否存在且进行中
    2. 获取分布式锁
    3. 调用Lua脚本原子扣减库存
    4. 生成订单号并返回
    """
    # 检查秒杀活动是否存在
    activity = db.query(SeckillActivity).filter(SeckillActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="秒杀活动不存在")
    
    # 检查秒杀活动状态
    if activity.status != 2:
        raise HTTPException(status_code=400, detail="秒杀活动未开始或已结束")
    
    # 检查时间
    import datetime
    now = datetime.datetime.now()
    if now < activity.start_time or now > activity.end_time:
        raise HTTPException(status_code=400, detail="秒杀活动时间已过")
    
    # 构建锁键和库存键
    lock_key = f"seckill:lock:{activity_id}"
    stock_key = f"seckill:stock:{activity_id}"
    
    # 获取分布式锁
    lock = RedisLock(redis_client, lock_key, expire=5)
    if not lock.acquire():
        raise HTTPException(status_code=429, detail="系统繁忙，请稍后重试")
    
    try:
        # 加载并执行Lua脚本
        lua_script = load_lua_script()
        script = redis_client.register_script(lua_script)
        
        # 执行脚本扣减库存
        result = script(keys=[stock_key])
        
        if result == -1:
            raise HTTPException(status_code=400, detail="库存不足")
        
        # 生成订单号
        order_id = str(uuid.uuid4())
        
        # 构建订单消息
        order_message = {
            "order_id": order_id,
            "activity_id": activity_id,
            "product_id": activity.product_id,
            "user_id": 1,  # 这里应该从用户认证中获取
            "quantity": 1,
            "amount": activity.seckill_price,
            "created_at": time.time()
        }
        
        # 发送消息到RabbitMQ队列
        try:
            rabbitmq_manager.publish_message(
                queue_name="seckill_orders",
                message=order_message
            )
            print(f"Order message sent to RabbitMQ: {order_id}")
        except Exception as e:
            print(f"Failed to send message to RabbitMQ: {e}")
        
        # 返回订单号和剩余库存
        return {
            "order_id": order_id,
            "remaining_stock": result,
            "message": "秒杀成功，订单正在处理中"
        }
    finally:
        # 释放锁
        lock.release()

# # 秒杀接口（异步版本）
# @router.post("/async/{activity_id}", summary="秒杀商品（异步）")
# async def seckill_async(
#     activity_id: int,
#     db: Session = Depends(get_db),
#     redis_client: aioredis.Redis = Depends(get_redis_client_async)
# ):
#     """
#     秒杀商品接口（异步版本）
#     1. 检查秒杀活动是否存在且进行中
#     2. 获取分布式锁
#     3. 调用Lua脚本原子扣减库存
#     4. 生成订单号并返回
#     """
#     # 检查秒杀活动是否存在
#     activity = db.query(SeckillActivity).filter(SeckillActivity.id == activity_id).first()
#     if not activity:
#         raise HTTPException(status_code=404, detail="秒杀活动不存在")
#     
#     # 检查秒杀活动状态
#     if activity.status != 2:
#         raise HTTPException(status_code=400, detail="秒杀活动未开始或已结束")
#     
#     # 检查时间
#     import datetime
#     now = datetime.datetime.now()
#     if now < activity.start_time or now > activity.end_time:
#         raise HTTPException(status_code=400, detail="秒杀活动时间已过")
#     
#     # 构建锁键和库存键
#     lock_key = f"seckill:lock:{activity_id}"
#     stock_key = f"seckill:stock:{activity_id}"
#     
#     # 获取分布式锁
#     lock = AsyncRedisLock(redis_client, lock_key, expire=5)
#     if not await lock.acquire():
#         raise HTTPException(status_code=429, detail="系统繁忙，请稍后重试")
#     
#     try:
#         # 加载并执行Lua脚本
#         lua_script = load_lua_script()
#         
#         # 执行脚本扣减库存
#         result = await redis_client.eval(lua_script, 1, stock_key)
#         
#         if result == -1:
#             raise HTTPException(status_code=400, detail="库存不足")
#         
#         # 生成订单号
#         order_id = str(uuid.uuid4())
#         
#         # 这里可以添加订单创建逻辑
#         # 例如：创建订单记录到数据库
#         
#         # 返回订单号和剩余库存
#         return {
#             "order_id": order_id,
#             "remaining_stock": result,
#             "message": "秒杀成功"
#         }
#     finally:
#         # 释放锁
#         await lock.release()
