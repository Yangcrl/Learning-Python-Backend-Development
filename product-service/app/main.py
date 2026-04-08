"""
商品服务主入口
"""

import time
import uuid
from fastapi import FastAPI, Request
from app.core.config import settings
from app.core.database import Base, engine
from app.api import product

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

# 服务ID
service_id = f"product-service-{str(uuid.uuid4())[:8]}"

@app.on_event("startup")
def startup_event():
    """
    服务启动时执行
    """
    # 注册服务到Consul
    if consul_service:
        consul_service.register_service(
            service_name="product-service",
            service_id=service_id,
            address="localhost",
            port=8001,
            tags=["product"],
            check={
                'HTTP': 'http://localhost:8001/health',
                'Interval': '10s',
                'Timeout': '5s'
            }
        )

@app.on_event("shutdown")
def shutdown_event():
    """
    服务关闭时执行
    """
    # 从Consul注销服务
    if consul_service:
        consul_service.deregister_service(service_id)

# 健康检查路由
@app.get("/health")
def health_check():
    return {"status": "healthy"}
