"""
商品服务模块
"""

from typing import Optional, List
from sqlalchemy.orm import Session
import json
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.redis_client import pool
import redis


class ProductService:
    """
    商品服务类
    """
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        根据ID获取商品
        """
        # 先从Redis缓存获取
        redis_client = redis.Redis(connection_pool=pool, decode_responses=True)
        cache_key = f"product:detail:{product_id}"
        cached_product = redis_client.get(cache_key)
        
        if cached_product:
            # 缓存命中
            print(f"缓存命中：{cache_key}")
            # 从缓存中获取商品信息
            product_data = json.loads(cached_product)
            # 构建商品对象
            product = Product(**product_data)
            return product
        
        # 缓存未命中，从数据库查询
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if product:
            # 将商品信息写入缓存
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "created_time": str(product.created_time)
            }
            redis_client.set(cache_key, json.dumps(product_dict), ex=300)  # 缓存5分钟
            print(f"缓存回写：{cache_key}")
        
        return product
    
    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        获取商品列表
        """
        return db.query(Product).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """
        创建商品
        """
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def update_product(db: Session, product_id: int, product: ProductUpdate) -> Optional[Product]:
        """
        更新商品
        """
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return None
        
        # 更新商品信息
        for key, value in product.model_dump(exclude_unset=True).items():
            setattr(db_product, key, value)
        
        db.commit()
        db.refresh(db_product)
        
        # 清除缓存
        redis_client = redis.Redis(connection_pool=pool, decode_responses=True)
        cache_key = f"product:detail:{product_id}"
        redis_client.delete(cache_key)
        print(f"缓存清除：{cache_key}")
        
        return db_product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        删除商品
        """
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return False
        
        db.delete(db_product)
        db.commit()
        
        # 清除缓存
        redis_client = redis.Redis(connection_pool=pool, decode_responses=True)
        cache_key = f"product:detail:{product_id}"
        redis_client.delete(cache_key)
        print(f"缓存清除：{cache_key}")
        
        return True
