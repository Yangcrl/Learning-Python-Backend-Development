"""
认证接口路由文件
对外提供用户认证相关的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.user_service import UserService

# 创建路由
router = APIRouter(
    prefix="/api/auth",  # 所有接口都以这个开头
    tags=["认证管理"]         # 接口文档里分组显示
)


# 注册接口
@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    """
    try:
        db_user = UserService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# 登录接口
@router.post("/login", response_model=Token, summary="用户登录")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    """
    # 验证用户
    db_user = UserService.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
