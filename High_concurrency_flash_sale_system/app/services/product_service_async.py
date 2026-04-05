"""
异步商品服务
提供异步的商品查询和缓存操作
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.core.redis_client_async import AsyncRedisCacheUtil
import aioredis

class AsyncProductService:
    """
    异步商品服务
    """
    
    @staticmethod
    async def get_product_with_cache(
            db: Session,
            redis_client: aioredis.Redis,
            product_id: int
    ) -> Optional[Product]:
        """
        异步获取商品信息，优先从缓存获取
        :param db: 数据库会话
        :param redis_client: Redis客户端
        :param product_id: 商品ID
        :return: 商品对象
        """
        # 构建缓存键
        cache_key = f"product:detail:{product_id}"
        
        # 尝试从缓存获取
        cached_product = await AsyncRedisCacheUtil.get_cache(redis_client, cache_key)
        if cached_product:
            # 缓存命中
            print(f"缓存命中：{cache_key}")
            # 转换为Product对象
            product = Product(**cached_product)
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
                "stock": product.stock
            }
            await AsyncRedisCacheUtil.set_cache(redis_client, cache_key, product_dict, expire=300)
            print(f"缓存回写：{cache_key}")
        
        return product
