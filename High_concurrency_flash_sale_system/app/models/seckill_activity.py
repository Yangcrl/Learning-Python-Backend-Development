"""
通过外键 product_id 关联商品，
定义了秒杀的价格、库存、时间、状态等关键参数，
并通过 relationship 实现了 “秒杀活动 → 商品” 的反向关联
"""

# 导入SQLAlchemy字段类型：列、整数、高精度小数、时间、外键
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
# 导入关系映射工具：建立表和表之间的关联
from sqlalchemy.orm import relationship
# 导入数据库内置函数：用于自动生成当前时间
from sqlalchemy.sql import func
# 导入数据库基类
from app.core.database import Base

# 定义秒杀活动表类
class SeckillActivity(Base):
    __tablename__ = 'seckill_activities'

    # 秒杀活动ID,主键，自增
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 关联商品ID，外键
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, comment='关联商品ID')

    # 秒杀价格
    seckill_price = Column(Numeric(10, 2), nullable=False, comment='秒杀价格')

    # 秒杀库存（和商品总库存stock分开）
    seckill_stock = Column(Integer, nullable=False, comment='秒杀库存')

    # 秒杀开始时间（判断，没到时间不能抢）
    start_time = Column(DateTime(timezone=True), nullable=False, comment='秒杀开始时间')

    # 秒杀结束时间（判断，过了时间不能抢）
    end_time = Column(DateTime(timezone=True), nullable=False, comment='秒杀结束时间')

    # 活动状态
    status = Column(Integer, default=1, comment='状态：1-未开始，2-进行中，3-已结束')

    # 创建时间
    created_time = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')

    # 多对一关系映射：多个秒杀活动对应一个商品
    product = relationship('Product', back_populates='seckill_activities')


