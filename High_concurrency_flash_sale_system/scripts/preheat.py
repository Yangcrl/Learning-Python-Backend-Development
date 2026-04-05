"""
库存预热脚本
将秒杀活动的库存加载到Redis中，使用hash结构存储
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis
from app.core.redis_client import pool
from app.core.database import get_db
from app.models import SeckillActivity

# 获取Redis连接
redis_client = redis.Redis(connection_pool=pool, decode_responses=True)

# 获取数据库会话
db = next(get_db())

try:
    # 查询所有进行中的秒杀活动
    activities = db.query(SeckillActivity).filter(SeckillActivity.status == 2).all()
    
    if not activities:
        print("没有进行中的秒杀活动")
    else:
        print(f"发现 {len(activities)} 个进行中的秒杀活动")
        
        for activity in activities:
            # 构建Redis键名
            stock_key = f"seckill:stock:{activity.id}"
            
            # 检查Redis中是否已有库存数据
            existing_stock = redis_client.hget(stock_key, "stock")
            
            if existing_stock:
                print(f"活动 {activity.id} 的库存已存在于Redis中，当前库存: {existing_stock}")
            else:
                # 将库存加载到Redis
                redis_client.hset(stock_key, "stock", activity.seckill_stock)
                redis_client.hset(stock_key, "product_id", activity.product_id)
                redis_client.hset(stock_key, "seckill_price", str(activity.seckill_price))
                
                # 设置过期时间（活动结束后2小时）
                expire_seconds = int((activity.end_time - activity.start_time).total_seconds()) + 7200
                redis_client.expire(stock_key, expire_seconds)
                
                print(f"活动 {activity.id} 的库存已预热到Redis中")
                print(f"  商品ID: {activity.product_id}")
                print(f"  秒杀价格: {activity.seckill_price}")
                print(f"  库存数量: {activity.seckill_stock}")
                print(f"  过期时间: {expire_seconds} 秒")
                
finally:
    db.close()
    redis_client.close()

print("\n库存预热完成！")
