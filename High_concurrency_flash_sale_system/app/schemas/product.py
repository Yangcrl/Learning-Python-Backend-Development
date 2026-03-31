"""
FastAPI接口的数据校验 + 数据格式规范
1. 前端传参必须按这个格式来（自动校验）
2. 后端返回数据必须按这个格式返回（自动格式化）
3. 区分请求/响应，保证安全、规范
"""

# Pydantic 基类，数据校验核心
from pydantic import BaseModel
# 时间类型（创建时间、更新时间）
from datetime import datetime
# 可选字段
from typing import Optional

# 商品基础模型
class ProductBase(BaseModel):
    name: str                           # 商品名称（必填，字符串）
    description: Optional[str] = None   # 描述（可选，不传就是 None）
    price: float                        # 价格（必填，必须是数字）
    stock: int                          # 库存（必填，必须是数字）

# 商品创建模型（前端新增商品时用）
class ProductCreate(ProductBase):
    """
    继承ProductBase，拥有全部四个字段：name, description, price, stock
    """
    pass

# 商品更新模型（前端修改商品时用）
class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

# 商品响应模型（后端返回给前端时用）
class ProductResponse(ProductBase):
    id: int                                 # 商品ID(数据库自增)
    created_time: datetime                  # 创建时间
    updated_time: Optional[datetime] = None # 更新时间

    class Config:
        from_attributes = True  # 把数据库ORM对象自动转成JSON返回给前端