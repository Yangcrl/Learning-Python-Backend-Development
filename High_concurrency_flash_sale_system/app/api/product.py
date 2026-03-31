"""
商品接口路由文件
对外提供服务的入口
定义接口地址（URL），接收前端参数，调用 Service 层做业务，返回标准格式数据
"""
from sys import prefix

# 路由、依赖、异常
from fastapi import APIRouter, Depends, HTTPException
# 数据库会话类型
from sqlalchemy.orm import Session
# 列表
from typing import List
# 获取数据库连接
from app.core.database import get_db
# 数据校验
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
# 业务逻辑
from app.services.product_service import ProductService

# 创建路由
router = APIRouter(
    prefix = "/api/products",  # 所有接口都以这个开头
    tags = ["商品管理"]         # 接口文档里分组显示
)

# 接口1：创建商品（POST）
@router.post("/", response_model=ProductResponse)
def create_product(
        product: ProductCreate,        # 接收前端参数（自动校验）
        db: Session = Depends(get_db)  # 自动拿数据库连接
):

# 接口2：根据 ID 获取单个商品（GET）
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
        product_id: int,  # 路径参数：商品ID
        db: Session = Depends(get_db)
):
    product = ProductService.get(db, product_id)

    # 如果没有找到商品
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    # 存在->返回商品信息
    return product

# 接口3：获取商品列表（GET）
@router.get("/", response_model=List[ProductResponse])
def list_products(
        skip: int = 0,      # 跳过数量（分页用）
        limit: int = 100,   # 最多返回数量
        db: Session = Depends(get_db)
):
    return ProductService.list(db, skip, limit)

# 接口4：更新商品信息（PUT）
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
        product_id: int,
        product: ProductUpdate,
        db: Session = Depends(get_db)
):
    updated = ProductService.update(db, product_id, product)

    if not updated:
        raise HTTPException(status_code=404, detail="商品不存在")

    return updated

# 接口5：删除商品（DELETE）
@router.delete("/{product_id}")
def delete_product(
        product_id: int,
        db: Session = Depends(get_db)
):
    success = ProductService.delete(db, product_id)

    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")

    return {"message": "商品已删除"}

