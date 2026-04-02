from app.core.bloom_filter import BloomFilter
from app.core.database import get_db
from app.models.product import Product
from sqlalchemy.orm import Session

# 初始化布隆过滤器
bloom_filter = BloomFilter(size=1000000, hash_count=5)

# 加载商品ID到布隆过滤器
def load_product_ids():
    db = next(get_db())
    try:
        products = db.query(Product).all()
        product_ids = {str(product.id) for product in products}
        bloom_filter.add_batch(product_ids)
        print(f"布隆过滤器初始化完成，加载了 {len(product_ids)} 个商品ID")
    finally:
        db.close()

# 获取布隆过滤器实例
def get_bloom_filter():
    return bloom_filter
