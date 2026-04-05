"""
数据准备脚本
用于在数据库中插入测试商品和秒杀活动数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Product, SeckillActivity
from datetime import datetime, timedelta

# 获取数据库会话
db = next(get_db())

try:
    # 检查是否已有商品数据
    existing_product = db.query(Product).filter(Product.id == 1).first()
    
    if not existing_product:
        # 创建测试商品
        product = Product(
            name="iPhone 15 Pro Max",
            description="2024款旗舰手机，A17 Pro芯片，钛金属机身",
            price=6999.00,
            stock=1000
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        print(f"创建商品成功：{product.name} (ID: {product.id})")
    else:
        product = existing_product
        print(f"商品已存在：{product.name} (ID: {product.id})")
    
    # 检查是否已有秒杀活动数据
    existing_activity = db.query(SeckillActivity).filter(SeckillActivity.id == 1).first()
    
    if not existing_activity:
        # 创建秒杀活动
        # 开始时间设为当前时间，结束时间设为1小时后
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        activity = SeckillActivity(
            product_id=product.id,
            seckill_price=4999.00,  # 秒杀价格
            seckill_stock=100,  # 秒杀库存
            start_time=start_time,
            end_time=end_time,
            status=2  # 2-进行中
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        print(f"创建秒杀活动成功：ID: {activity.id}")
        print(f"  商品：{product.name}")
        print(f"  秒杀价格：{activity.seckill_price}")
        print(f"  秒杀库存：{activity.seckill_stock}")
        print(f"  开始时间：{activity.start_time}")
        print(f"  结束时间：{activity.end_time}")
    else:
        activity = existing_activity
        print(f"秒杀活动已存在：ID: {activity.id}")
        print(f"  商品：{activity.product.name}")
        print(f"  秒杀价格：{activity.seckill_price}")
        print(f"  秒杀库存：{activity.seckill_stock}")
        print(f"  开始时间：{activity.start_time}")
        print(f"  结束时间：{activity.end_time}")
        print(f"  状态：{activity.status}")
        
finally:
    db.close()

print("\n数据准备完成！")
