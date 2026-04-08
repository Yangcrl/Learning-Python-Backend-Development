from fastapi import FastAPI
from contextlib import asynccontextmanager
import uuid

from app.core.config import settings
from app.core.database import engine, Base
from app.api import order

# 导入Consul服务
try:
    import sys
    sys.path.append('..')
    from High_concurrency_flash_sale_system.app.core.consul_service import consul_service
except Exception as e:
    print(f"Failed to import Consul service: {e}")
    consul_service = None

# 服务ID
service_id = f"order-service-{str(uuid.uuid4())[:8]}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    
    # 注册服务到Consul
    if consul_service:
        consul_service.register_service(
            service_name="order-service",
            service_id=service_id,
            address="localhost",
            port=8002,
            tags=["order"],
            check={
                'HTTP': 'http://localhost:8002/health',
                'Interval': '10s',
                'Timeout': '5s'
            }
        )
    
    yield
    
    # Shutdown
    # 从Consul注销服务
    if consul_service:
        consul_service.deregister_service(service_id)


app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="订单服务 API",
    lifespan=lifespan
)

app.include_router(order.router, prefix="/api/orders", tags=["orders"])


@app.get("/")
async def root():
    return {"message": "Order Service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
