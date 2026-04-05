"""
配置管理模块
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    # 项目名称
    PROJECT_NAME: str = "Product Service"
    # 版本
    VERSION: str = "1.0.0"
    # API前缀
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/seckill"
    
    # Redis配置
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "123456"
    REDIS_DB: int = 0
    
    # gRPC配置
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50052
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
