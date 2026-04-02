"""
负责商品的增删改查（CRUD）
所有数据库操作都在这里，接口层只负责调用
"""

# 数据库会话
from sqlalchemy.orm import Session


# 商品数据库模型
from app.models.product import Product
# Pydantic 校验模型
from app.schemas.product import ProductCreate, ProductUpdate
# 类型注释：列表、可选值
from typing import List, Optional

from redis import Redis
from app.core.redis_client import RedisCacheUtil

"""缓存配置"""
# 商品详情缓存key前缀，命名规范：业务:模块:id
PRODUCT_DETAIL_CACHE_KEY = "product:detail:"
# 商品缓存过期时间，10分钟=600秒
PRODUCT_DETAIL_CACHE_EXPIRE = 600

# 服务类：ProductService
class ProductService:
    # 创建商品
    @staticmethod
    def create(db: Session, product_in: ProductCreate) -> Product:
        """
        创建商品
        :param db: 数据库会话
        :param product_in: 商品信息
        :return: 创建成功的商品
        """
        # 把 Pydantic 模型 -> 数据库模型
        db_product = Product(**product_in.model_dump())
        # 添加到数据库会话
        db.add(db_product)
        # 提交事务
        db.commit()
        # 刷新对象（获取自动生成的 id、创建时间）
        db.refresh(db_product)
        # 返回创建好的商品
        return db_product

    @staticmethod
    def get(db: Session, product_id: int) -> Optional[Product]:
        """
        根据ID查询单个商品
        :param db: 数据库会话
        :param product_id: 商品ID
        :return: 商品信息
        """
        # 通过商品ID查询商品
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def list(db: Session, skip: int=0, limit: int=100) -> List[Product]:
        """
        查询商品列表（分页）
        :param db: 数据库会话
        :param skip: 跳过数量
        :param limit: 查询数量
        :return: 商品列表
        """
        return db.query(Product).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, product_id: int, product_in: ProductUpdate) -> Optional[Product]:
        """
        更新商品信息
        :param db: 数据库会话
        :param product_id: 商品ID
        :param product_in: 商品信息
        :return: 更新后的商品信息
        """
        # 查询商品是否存在
        db_product = db.query(Product).filter(Product.id == product_id).first()
        # 不存在返回 None
        if not db_product:
            return None

        # 只获取前端传了的字段
        update_data = product_in.model_dump(exclude_unset=True)

        # 循环更新字段
        for field, value in update_data.items():
            setattr(db_product, field, value)

        # 提交更新
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete(db: Session, product_id: int) -> bool:
        """
        删除商品
        :param db: 数据库会话
        :param product_id: 商品ID
        :return: 删除结果
        """
        # 查存在性
        db_product = db.query(Product).filter(Product.id == product_id).first()
        # 不存在返回 False
        if not db_product:
            return False

        # 删除
        db.delete(db_product)
        db.commit()
        return True

    # 带缓存的商品详情查询
    @staticmethod
    def get_product_with_cache(
            db: Session,
            redis_client: Redis,
            product_id: int
    ) -> Optional[Product]:
        """
        商品详情查询，旁路缓存模式实现
        1. 先查 Redis 缓存，命中直接返回
        2. 缓存未命中，查询 MySQL 数据库
        3. 数据库查到数据，回写 Redis 缓存，设置过期时间
        4. 返回数据
        :param db: 数据库会话，用来查 MySQL
        :param redis_client: Redis 客户端，用来读写缓存
        :param product_id: 要查询的商品的ID
        :return: 查到则返回商品字典，否则返回None
        """
        # 拼接缓存key
        cache_key = f'{PRODUCT_DETAIL_CACHE_KEY}{product_id}'

        # 先查 Redis 缓存
        cache_data = RedisCacheUtil.get_cache(redis_client, cache_key)
        if cache_data:
            # 缓存命中，直接返回
            print(f'缓存命中，商品ID={product_id}')
            return cache_data

        # 缓存未命中，查询 MySQL 数据库
        print(f'缓存未命中，商品ID={product_id}，查询数据库...')
        db_product = db.query(Product).filter(Product.id == product_id).first()

        # 数据库无数据，直接返回 None
        if not db_product:
            print(f'数据库无数据，商品ID={product_id}')
            return None

        # 数据库有数据，转为字典
        product_dict = {
            'id': db_product.id,
            'name': db_product.name,
            'description': db_product.description,
            'price': float(db_product.price),
            'stock': db_product.stock,
            'created_time': db_product.created_time.isoformat() if db_product.created_time else None,
            'updated_time': db_product.updated_time.isoformat() if db_product.updated_time else None
        }

        # 回写 Redis 缓存，设置过期时间
        RedisCacheUtil.set_cache(
            redis_client,
            cache_key,
            product_dict,
            expire=PRODUCT_DETAIL_CACHE_EXPIRE
        )
        print(f'缓存回写，商品ID={product_id}，已写入Redis缓存')

        # 返回数据
        return product_dict

    # 带缓存清理的商品更新
    @staticmethod
    def update_product_with_cache(
            db: Session,
            redis_client: Redis,
            product_id: int,
            product_in: ProductUpdate
    ) -> Optional[Product]:
        """
        更新商品：先更新数据库，再删除缓存，保证数据一致性
        :param db: 数据库连接对象
        :param redis_client: Redis 客户端对象
        :param product_id: 商品唯一标识
        :param product_in: 商品入参数据
        :return: 更新成功返回Product商品对象，失败返回None
        """
        # 查询商品是否存在
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return None

        # 更新数据库
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)

        # 删除旧缓存，下次读请求会回写最新数据
        cache_key = f'{PRODUCT_DETAIL_CACHE_KEY}{product_id}'
        RedisCacheUtil.delete_cache(redis_client, cache_key)
        print(f'缓存清理，商品ID={product_id}，旧缓存已删除')

        # 返回更新后的商品对象
        return db_product

    # 带缓存清理的商品删除
    @staticmethod
    def delete_product_with_cache(
            db: Session,
            redis_client: Redis,
            product_id: int
    ) -> bool:
        """
        删除商品：先删除数据库，再删除缓存，保证数据一致性
        :param db: 数据库连接对象
        :param redis_client: Redis 客户端对象
        :param product_id: 删除的商品ID
        :return: 删除成功返回True，失败返回False
        """
        # 查询商品是否存在
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return False

        # 删除数据库数据
        db.delete(db_product)
        db.commit()

        # 删除缓存
        cache_key = f'{PRODUCT_DETAIL_CACHE_KEY}{product_id}'
        RedisCacheUtil.delete_cache(redis_client, cache_key)
        print(f'缓存清理，商品ID={product_id}，缓存已删除')

        return True