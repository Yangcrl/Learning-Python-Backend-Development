"""
这是秒杀系统的商品表模型，定义了商品的所有属性（名称、价格、库存等），并通过 relationship 建立了 “一个商品对应多个秒杀活动” 的一对多关系，是整个秒杀业务的核心数据基础！
"""

# 导入SQLAlchemy字段类型：列、整数、字符串、高精度小数、时间、长文本
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
# 导入关系映射工具：用于建立表和表之间的关联
from sqlalchemy.orm import relationship
# 导入数据库内置函数：用于自动生成当前时间
from sqlalchemy.sql import func
# 导入数据库基类（所有表模型都必须继承这个Base）
from app.core.database import Base

# 定义商品表类
class Product(Base):
    # 指定MySQL中的表名
    __tablename__ = 'products'

    # 定义商品ID列
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 定义商品名称列
    name = Column(String(100), nullable=False, comment='商品名称')

    # 商品描述
    description = Column(Text, comment='商品描述')

    # 商品原价
    price = Column(Numeric(10, 2), nullable=False, comment='商品原价')

    # 商品总库存(常规库存）
    stock = Column(Integer, default=0, comment='商品总库存')

    # 创建时间
    created_time = Column(DateTime(timezone=True), server_default=func.now())

    # 更新时间
    updated_time = Column(DateTime(timezone=True), onupdate=func.now())

    # 一对多关系映射：一个商品对应多个秒杀活动
    seckill_activities = relationship('SeckillActivity', back_populates='product')