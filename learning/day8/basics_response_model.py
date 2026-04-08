# 导入库
from fastapi import FastAPI
from pydantic import BaseModel

# 创建FastAPI实例
app = FastAPI()

# 定义输入模型UserIn：接收用户注册时的数据
class UserIn(BaseModel):
    username: str # 用户名
    password: str # 密码
    email: str # 邮箱

# 定义输出模型UserOut：返回给前端的数据
class UserOut(BaseModel):
    username: str # 只返回用户名
    email: str # 只返回邮箱
    # 不返回密码

# 模拟一个数据库（用列表代替，真实开发用MySQL/Redis）
fake_db = []

# 实现POST/users接口
# response_model=UserOut表示返回数据必须符合UserOut模型
@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    # 把用户输入的数据存到数据库里
    fake_db.append(user)

    # 返回用户输入的数据
    # FastAPI会自动用UserOut模型对返回的数据进行过滤，只返回用户名、邮箱
    return user