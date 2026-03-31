"""
用户安全认知
负责：密码加密、生成登录令牌、验证身份、获取当前用户
"""

# 导入依赖
from datetime import datetime, timedelta            # 时间工具：生成令牌过期时间
from jose import jwt, JWTError                      # JWT令牌：生成/解析/报错
from passlib.context import CryptContext            # 密码加密：bcrypt算法
from fastapi import Depends, HTTPException, status  # FastAPI依赖/异常/状态码
from fastapi.security import OAuth2PasswordBearer   # OAuth2标准：获取令牌
from sqlalchemy.orm import Session                  # 数据库会话：查询用户
from app.core.config import settings                # 配置文件：密钥/过期时间
from app.core.database import get_db                # 数据库连接
from app.models.user import User                    # 用户表模型

# 全局初始化
# 密码加密器：使用bcrypt行业标准加密算法  bcrypt：不可逆加密  自动处理过期算法
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# OAuth2认证规则：告诉系统登录接口是 /api/auth/login  自动从请求头拿Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')

# 验证密码
def verify_password(plain: str, hashed:str):
    """
    :param plain: 用户输入的明文密码
    :param hashed: 数据库里存的加密密码
    :return: True=密码正确，False=错误
    """
    plain_bytes = plain.encode('utf-8')
    if len(plain_bytes) > 72:
        plain_bytes = plain_bytes[:72]
        plain = plain_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain, hashed)

# 加密密码
def get_hash(password: str):
    """
    :param password: 用户输入的明文密码
    :return: 加密后的密码
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

# 生成JWT登录令牌
def create_token(data: dict):
    """
    :param data: 登录用户信息
    :return: 登录令牌
    """
    # 计算过期时间：当前时间 + 30分钟 timedelta: 时间间隔
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 把过期时间加入令牌数据
    data.update({"exp": expire})

    # 生成令牌：用密钥 + 算法加密
    return jwt.encode(
        data,                         # 令牌数据
        settings.SECRET_KEY,          # 密钥
        algorithm=settings.ALGORITHM  # 加密算法
    )

# 获取当前登录用户
def get_current_user(
        token: str = Depends(oauth2_scheme),  # 自动从请求头拿Token
        db: Session = Depends(get_db)         # 自动获取数据库连接
):
    try:
        # 解析Token（用密钥解密）
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # 从令牌里取出用户名
        username = payload.get("sub")

        # 没有用户名 = 无效令牌
        if not username:
            raise HTTPException(401, '无效凭证')

    # Token伪造/过期/错误 直接报错
    except JWTError:
        raise HTTPException(401, '无效凭证')

    # 去数据库查询这个用户
    user = db.query(User).filter(User.username == username).first()

    # 用户不存在 报错
    if not user:
        raise HTTPException(401, '用户不存在')

    # 验证通过，返回当前登录用户
    return user
