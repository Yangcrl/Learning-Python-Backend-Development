"""
database 连接配置
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Generator

# 创建数据库引擎
# 优化连接池配置
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=10,        # 最大溢出连接数
    pool_pre_ping=True,      # 连接前 ping 检查
    pool_recycle=3600,       # 连接回收时间（秒）
    echo=False               # 是否打印 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

"""
fastapi 依赖注入：获取数据库会话
"""
def get_db() -> Generator:
    """
    fastapi 接口依赖注入用，自动创建数据库会话，用完自动关闭
    用法：在接口参数里写 db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
