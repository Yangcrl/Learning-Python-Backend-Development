from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

# 定义一个商品模型
class Product(BaseModel):
    product_id: int = Field(alias="id") # 别名：数据库里叫 id，返回给前端叫 product_id
    name: str
    price: float
    description: str = None # 商品简介，默认值是None
    stock: int = 0 # 库存，默认值是0

# 模拟一个商品数据
sample_product = {
    "id": 1,
    "name": "Apple iPhone 15 Pro",
    "price": 9999.99,
    "stock": 100
}

# response_model_include: 只返回name和price
@app.get("/product/short", response_model=Product, response_model_include={"name", "price"})
async def get_product_short():
    return sample_product

# response_model_exclude: 排除price（不返回价格）
@app.get("/product/no_price", response_model=Product, response_model_exclude="price")
async def get_product_no_price():
    return sample_product

# response_model_exclude_unset: 只返回有值的字段
# 因为description没设置，返回结果里会自动消失
@app.get("/product/clean", response_model=Product, response_model_exclude_unset=True)
async def get_product_clean():
    return sample_product

# response_model_exclude_alias: 使用别名返回
@app.get("/product/alias", response_model=Product, response_model_by_alias=True)
async def get_product_alias():
    return sample_product
