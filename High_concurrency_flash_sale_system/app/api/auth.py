"""
负责：用户注册，用户登录，获取当前登录用户信息
"""

# 导入依赖
"""把之前写的数据库、安全、模型、校验工具全部引入，实现接口功能"""
# FastAPI路由、依赖注入、异常抛出
from fastapi import APIRouter, Depends, HTTPException
# 数据库会话类型
from sqlalchemy.orm import Session
# 数据库连接工具（获取会话）
from app.core.database import get_db
# 安全工具：加密、验密、生成token、获取当前用户
from app.core.security import get_hash, verify_password, create_token, get_current_user
# 数据库用户表模型
from app.models.user import User
# 数据校验模型
from app.schemas.user import UserCreate, UserResponse, Token

# 创建路由实例（接口统一管理）
router = APIRouter(
    prefix = "/api/auth",  # 接口统一前缀：所有接口都以 /api/auth 开头
    tags = ["用户认证"]     # 接口文档分组：Swagger 里归类显示
)

# 注册接口：POST请求，响应数据格式为 UserResponse（无密码）
@router.post("/register", response_model = UserResponse)
def register(
        # 接收前端参数：自动用 UserCreate 校验格式（用户名+ 密码）
        user: UserCreate,
        # 自动获取数据库连接（依赖注入，不用手写连接代码）
        db: Session = Depends(get_db)
):
    # 查询数据库：用户名是否已被注册
    exists = db.query(User).filter(User.username == user.username).first()

    # 如果用户名已经存在 则抛出400异常
    if exists:
        raise HTTPException(400, '用户名已存在')

    # 创建新用户：密码加密存储
    new_user = User(
        username = user.username,
        password = get_hash(user.password)  # 调用安全工具加密
    )

    # 把用户数据加入数据库会话
    db.add(new_user)

    # 提交事务，真正写入MySQL
    db.commit()

    # 刷新对象，获取数据库自动生成的ID、创建时间
    db.refresh(new_user)

    # 返回用户信息（自动按UserResponse格式，隐藏密码）
    return new_user

# 登录接口：POST请求，响应数据格式为 Token
@router.post("/login", response_model = Token)
def login(
        user: UserCreate,
        db: Session = Depends(get_db)
):

    # 根据用户名查询数据库用户
    db_user = db.query(User).filter(User.username == user.username).first()

    # 验证：用户不存在 或 密码错误，抛出401无权限异常
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, '用户名或密码错误')

    # 验证成功则生成jwt登录令牌（存入用户名）
    token = create_token({"sub": db_user.username})

    # 返回标准令牌格式（前端存储令牌，后续请求携带）
    return {"access_token": token, "token_type": "bearer"}

# 获取个人信息：GET请求，必须登录才能访问
@router.get("/me", response_model = UserResponse)
def me(
        # 核心：自动验证Token，获取当前登录用户（依赖注入鉴权）
        user: User = Depends(get_current_user)
):
    # 直接返回用户信息（安全：无密码）
    return user