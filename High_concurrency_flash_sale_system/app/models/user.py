"""
用户表模型，用Python类定义数据库表结构，自动建表，自动管理用户数据
"""

# 导入SQLAlchemy字段类型：列、整数、字符串、时间
from sqlalchemy import Column, Integer, String, DateTime
# 导入数据库内置函数（用于获取当前时间）
from sqlalchemy.sql import func
# 导入数据库基类（所有表模型都必须继承这个Base）
from app.core.database import Base

# 定义User类 = 数据库中的users表
class User(Base):
    # 指定MySQL中的表名：users
    __tablename__ = "users"

    # ===表字段（一列对应一个变量）===
    # 用户id：主键，自增，唯一标识
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用户名：字符串最长10，不可重复，不能为空
    username = Column(String(10), unique=True, nullable=False, comment = "用户名")
    # 密码：存储哈希后的密码（绝不存明文），最长255
    password = Column(String(255), nullable=False, comment = "密码")
    # 创建时间：带时区，数据库自动生成当前时间
    created_time = Column(DateTime(timezone=True), server_default=func.now(), comment = "创建时间")