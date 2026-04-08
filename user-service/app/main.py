"""
用户服务主入口
"""

import time
import uuid
from fastapi import FastAPI, Request
from app.core.config import settings
from app.core.database import Base, engine
from app.api import auth
from app.core.grpc_server import start_grpc_server

# 导入Consul服务
try:
    import sys
    sys.path.append('..')
    from High_concurrency_flash_sale_system.app.core.consul_service import consul_service
except Exception as e:
    print(f"Failed to import Consul service: {e}")
    consul_service = None

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
# 服务ID
service_id = f"user-service-{str(uuid.uuid4())[:8]}"

@app.on_event("startup")
def startup_event():
    """
    服务启动时执行
    """
    global grpc_server
    grpc_server = start_grpc_server()
    
    # 注册服务到Consul
    if consul_service:
        consul_service.register_service(
            service_name="user-service",
            service_id=service_id,
            address="localhost",
            port=8000,
            tags=["user", "grpc"],
            check={
                'HTTP': 'http://localhost:8000/health',
                'Interval': '10s',
                'Timeout': '5s'
            }
        )

@app.on_event("shutdown")
def shutdown_event():
    """
    服务关闭时执行
    """
    if grpc_server:
        grpc_server.stop(0)
        print("gRPC server stopped")
    
    # 从Consul注销服务
    if consul_service:
        consul_service.deregister_service(service_id)

# 健康检查路由
@app.get("/health")
def health_check():
    return {"status": "healthy"}
