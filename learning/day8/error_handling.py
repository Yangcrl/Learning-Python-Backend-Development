from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from basics_response_model import fake_db

app = FastAPI()

# 自定义异常类
class NotFoundError(Exception):
    """当找不到资源时抛出的异常"""
    def __init__(self, item_id: int):
        self.item_id = item_id # 保存找不到的ID，方便后面返回

# 注册错误拦截器
# 拦截自定义的NotFoundError异常
@app.exception_handler(NotFoundError)
async def handle_not_found(request, exc: NotFoundError):
    # 返回统一的错误格式
    return JSONResponse(
        status_code = 404, # HTTP状态码：404表示未找到
        content = {
            "code": 404,
            "msg": f"错误：ID 为{exc.item_id} 的用户不存在",
            "data": None
        }
    )
# 拦截FastAPI自带的HTTPException
@app.exception_handler(HTTPException)
async def handle_http_exception(request, exc: HTTPException):
    return JSONResponse(
        status_code = exc.status_code,
        content = {
            "code": exc.status_code,
            "msg": exc.detail,
            "data": None
        }
    )

# 模拟数据库和接口
fake_db = {1: "张三", 2: "李四", 3: "王五"}

class UserOut(BaseModel):
    id:  int
    name: str

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # 检查用户是否存在
    if user_id not in fake_db:
        raise NotFoundError(user_id)
    return {
        "code": 200,
        "msg": "成功",
        "data": {"id": user_id, "name": fake_db[user_id]}
    }
