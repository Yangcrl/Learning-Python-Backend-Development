from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import order


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


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
