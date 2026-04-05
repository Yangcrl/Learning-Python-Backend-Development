"""
职责： 项目的数据库连接工具
1. 跟MySQL建立连接
2. 创建数据库会话（操作窗口）
3. 给接口提供安全的数据库连接
4. 自动管理连接开关，防止泄露
"""

# 导入SQLAlchemy核心工具
from sqlalchemy import create_engine  # 创建数据库连接引擎
from sqlalchemy.orm import sessionmaker  # 创建数据库会话（操作窗口）
from sqlalchemy.ext.declarative import declarative_base  # ORM模型基类
from app.core.config import settings  # 导入配置文件（拿数据库地址）

# 创建数据库连接引擎
# 优化连接池配置
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=10,        # 最大溢出连接数
    pool_pre_ping=True,      # 连接前 ping 检查
    pool_recycle=3600,       # 连接回收时间（秒）
    echo=False               # 是否打印 SQL 语句
)

# 创建数据库会话（操作窗口）
SessionLocal = sessionmaker(
    autocommit=False,  # 不自动提交事务（必须手动commit才保存数据）
    autoflush=False,   # 不自动刷新（避免误操作修改数据库）
    bind=engine        # 绑定到上面创建的数据库通道
)

# 创建ORM模型基类（所有表的父类）
Base = declarative_base()

# FastAPI数据库依赖，给接口提供数据库会话
def get_db():
    # 创建一个新的数据库会话（打开窗口）
    db = SessionLocal()
    try:
        # 把会话交给接口使用（yield = 生成器，暂停在这里）
        yield db
    finally:
        # 无论接口成功/失败，最后一定关闭会话（关闭窗口）
        db.close()