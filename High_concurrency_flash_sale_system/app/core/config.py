# 导入配置工具
from pydantic_settings import BaseSettings

# 创建项目配置类（所有核心参数都在这里）
class Settings(BaseSettings):
    # 数据库连接配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/seckill"

    # JWT用户认证配置
    # 密钥：加密用户登录令牌（Token）的密码
    SECRET_KEY: str = "seckill_project_2026_secret_key"
    # 加密算法
    ALGORITHM: str = "HS256"
    # 令牌有效期：登录凭证30分钟后失效，保证安全
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# 创建配置实例（项目所有地方都用这个实例读取配置）
settings = Settings()