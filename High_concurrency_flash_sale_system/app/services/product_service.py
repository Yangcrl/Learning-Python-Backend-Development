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