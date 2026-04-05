from fastapi import FastAPI, Request
import time
from app.core.database import Base, engine
from app.api.auth import router as auth_router
from app.api.product import router as product_router
from app.api.seckill import router as seckill_router
from app.core.bloom_filter_manager import load_product_ids
from app.core.middleware import rate_limit_middleware

# 自动创建所有表
Base.metadata.create_all(bind=engine)

# 初始化布隆过滤器
load_product_ids()

app = FastAPI(title="高并发秒杀系统", version="1.0")

# 注册限流中间件
app.middleware("http")(rate_limit_middleware)

# 请求耗时中间件
@app.middleware("http")
async def add_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response

# 挂载路由
app.include_router(auth_router)

# 根路由
@app.get("/")
def index():
    return {"msg": "秒杀系统 Day5 完成！分布式锁和限流已实现"}

# 挂载路由
app.include_router(product_router)
app.include_router(seckill_router)