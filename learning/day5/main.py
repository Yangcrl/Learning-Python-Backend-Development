# 导入FastAPI类
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

# 创建FastAPI实例
app = FastAPI()

# 定义根路由的GET 请求处理函数
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# 自定义路由
@app.get("/test/hello")
async def hello():
    return {"message": "你好 FastAPI"}

# 路径参数
@app.get("/book/{b_id}")
async def get_book(b_id: int = Path(..., gt=0, lt=101, description="书籍ID，取值范围0-100")): # gt 大于 0, lt 小于 101
    return {"b_id": b_id, "title": f"这是第{b_id}本书"}

# 需求：查找书籍的作者，路径参数：name，长度范围：2-10
@app.get("/author/{name}")
async def get_name(name: str = Path(..., min_length=2, max_length=10)):
    return {"msg": f"作者名称：{name}"}

# 需求：查询新闻 -> 分页，skip：跳过的记录数， limit：返回的记录数 10
@app.get("/news/list")
async def get_news(
    skip: int = Query(0, description="跳过的记录数", lt=100),
    limit: int = Query(10, description="返回的记录数")
):
    return {"msg": "获取新闻列表成功","data": {"skip": skip, "limit": limit}}

# 注册：用户名和密码 str
class User(BaseModel):
    username: str = Field(default="张三", min_length=2, max_length=10, description="用户名")
    password: str = Field(min_length=3, max_length=20)

@app.post("/register")
async def register(user: User):
    return user


# main.py 最后一行
if __name__ == "__main__":
    # 打印所有已注册的路由路径
    routes = [route.path for route in app.routes]
    print("已注册的路由：", routes)