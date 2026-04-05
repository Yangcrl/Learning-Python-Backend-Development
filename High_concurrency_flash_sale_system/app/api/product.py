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
from redis import Redis
from app.core.redis_client import get_redis_client
from app.core.bloom_filter_manager import get_bloom_filter

# 获取布隆过滤器实例
bloom_filter = get_bloom_filter()

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
    product = ProductService.create(db, product)
    # 添加新商品ID到布隆过滤器
    bloom_filter.add(str(product.id))
    return product

# 接口2：根据 ID 获取单个商品（GET）- 带缓存
@router.get("/{product_id}", response_model=ProductResponse, summary="获取商品详情")
def get_product(
        product_id: int,
        db: Session = Depends(get_db),
        redis_client: Redis = Depends(get_redis_client)
):
    """
    商品详情接口，采用旁路缓存模式
    1. 首先通过布隆过滤器判断商品是否存在，防止缓存穿透
    2. 第一次请求：缓存未命中，查数据库，回写缓存，返回数据
    3. 后续请求：缓存命中，直接返回 Redis 数据，不查数据库
    """
    # 使用布隆过滤器防止缓存穿透
    if not bloom_filter.contains(str(product_id)):
        raise HTTPException(status_code=404, detail="商品不存在")
    
    product = ProductService.get_product_with_cache(db, redis_client, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

# 接口3：获取商品列表（GET）
@router.get("/", response_model=List[ProductResponse])
def list_products(
        skip: int = 0,      # 跳过数量（分页用）
        limit: int = 100,   # 最多返回数量
        db: Session = Depends(get_db)
):
    return ProductService.list(db, skip, limit)

# 接口4：更新商品信息（PUT）- 带缓存清理
@router.put("/{product_id}", response_model=ProductResponse, summary="更新商品信息")
def update_product(
        product_id: int,
        product_in: ProductUpdate,
        db: Session = Depends(get_db),
        redis_client: Redis = Depends(get_redis_client)
):
    updated_product = ProductService.update_product_with_cache(db, redis_client, product_id, product_in)
    if not updated_product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return updated_product

# 接口5：删除商品（DELETE）- 带缓存清理
@router.delete("/{product_id}")
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        redis_client: Redis = Depends(get_redis_client)
):
    success = ProductService.delete_product_with_cache(db, redis_client, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"message": "商品已删除"}

# # 接口6：获取商品详情（异步版本）
# @router.get("/async/{product_id}", response_model=ProductResponse, summary="获取商品详情（异步）")
# async def get_product_async(
#         product_id: int,
#         db: Session = Depends(get_db),
#         redis_client: aioredis.Redis = Depends(get_redis_client_async)
# ):
#     """
#     商品详情接口（异步版本），采用旁路缓存模式
#     1. 首先通过布隆过滤器判断商品是否存在，防止缓存穿透
#     2. 第一次请求：缓存未命中，查数据库，回写缓存，返回数据
#     3. 后续请求：缓存命中，直接返回 Redis 数据，不查数据库
#     """
#     # 使用布隆过滤器防止缓存穿透
#     if not bloom_filter.contains(str(product_id)):
#         raise HTTPException(status_code=404, detail="商品不存在")
#     
#     product = await AsyncProductService.get_product_with_cache(db, redis_client, product_id)
#     if not product:
#         raise HTTPException(status_code=404, detail="商品不存在")
#     return product

