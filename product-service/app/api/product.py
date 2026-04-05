"""
商品接口路由文件
对外提供商品相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

# 创建路由
router = APIRouter(
    prefix="/api/products",  # 所有接口都以这个开头
    tags=["商品管理"]         # 接口文档里分组显示
)


# 接口1：获取商品列表
@router.get("", response_model=List[ProductResponse], summary="获取商品列表")
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取商品列表
    """
    products = ProductService.get_products(db, skip=skip, limit=limit)
    return products


# 接口2：获取商品详情
@router.get("/{product_id}", response_model=ProductResponse, summary="获取商品详情")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    获取商品详情
    """
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return product


# 接口3：创建商品
@router.post("", response_model=ProductResponse, summary="创建商品")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    创建商品
    """
    return ProductService.create_product(db, product)


# 接口4：更新商品
@router.put("/{product_id}", response_model=ProductResponse, summary="更新商品")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    更新商品
    """
    db_product = ProductService.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return db_product


# 接口5：删除商品
@router.delete("/{product_id}", summary="删除商品")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    删除商品
    """
    success = ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return {"message": "商品已删除"}
