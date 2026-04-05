"""
用户服务主入口
"""

import time
from fastapi import FastAPI, Request
from app.core.config import settings
from app.core.database import Base, engine
from app.api import auth
from app.core.grpc_server import start_grpc_server

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册路由
app.include_router(auth.router)

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
        "message": "User Service is running",
        "version": settings.VERSION,
        "grpc_port": settings.GRPC_PORT
    }

# 启动gRPC服务
grpc_server = None

@app.on_event("startup")
def startup_event():
    """
    服务启动时执行
    """
    global grpc_server
    grpc_server = start_grpc_server()

@app.on_event("shutdown")
def shutdown_event():
    """
    服务关闭时执行
    """
    if grpc_server:
        grpc_server.stop(0)
        print("gRPC server stopped")
