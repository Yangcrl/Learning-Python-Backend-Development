"""
配置管理模块
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    # 项目名称
    PROJECT_NAME: str = "User Service"
    # 版本
    VERSION: str = "1.0.0"
    # API前缀
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/seckill"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # gRPC配置
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
