"""
商品服务主入口
"""

import time
from fastapi import FastAPI, Request
from app.core.config import settings
from app.core.database import Base, engine
from app.api import product

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册路由
app.include_router(product.router)

# 请求耗时中间件
@app.middleware("http")
async def add_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response

# 根路由
@app.get("/")
def index():
    return {
        "message": "Product Service is running",
        "version": settings.VERSION,
        "grpc_port": settings.GRPC_PORT
    }
