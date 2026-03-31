"""
用户认证模块
作用：定义接口的请求 / 响应数据格式、自动做数据验证、规范数据传输
"""

# 导入依赖
from pydantic import BaseModel  # pydantic的核心基类，所有数据模型都必须继承它
from datetime import datetime   # Python内置时间类型，用于处理创建时间

# 基础用户信息
# 抽取所有用户模型的公共字段，实现代码复用
class UserBase(BaseModel):
    username: str

# 注册/登录请求
# 继承UserBase，自动拥有username字段，新增字段：password（密码）
# 接收前端注册/登录传来的请求数据
class UserCreate(UserBase):
    password: str

# Token返回
class Token(BaseModel):
    access_token: str  # 访问令牌（JWT字符串）
    token_type: str    # 令牌类型（固定为bearer）

# 用户响应
class UserResponse(UserBase):
    id: int                 # 用户唯一ID（数据库自增ID）
    created_time: datetime  # 用户创建时间

    class Config:
        from_attributes = True  # 让Pydantic直接读取数据库ORM模型，把数据库数据自动转换成接口响应数据



