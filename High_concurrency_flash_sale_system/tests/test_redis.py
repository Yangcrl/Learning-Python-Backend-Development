# test_redis.py
from app.core.redis_client import get_redis_client, RedisCacheUtil

# 获取Redis连接
redis_client = next(get_redis_client())

# ====================== 测试1：写入商品缓存 ======================
product_data = {
    "id": 1,
    "name": "iPhone 15 Pro Max",
    "price": 7999.00,
    "stock": 100,
    "description": "2024新款苹果手机",
    "created_at": "2024-04-01 12:00:00"
}
# 写入缓存，10分钟过期
success = RedisCacheUtil.set_cache(redis_client, "product:detail:1", product_data, expire=600)
print(f"写入缓存结果: {success}")

# ====================== 测试2：读取商品缓存 ======================
cache_data = RedisCacheUtil.get_cache(redis_client, "product:detail:1")
print(f"读取到的缓存数据: {cache_data}")

# ====================== 测试3：检查key是否存在 ======================
is_exist = RedisCacheUtil.is_exist(redis_client, "product:detail:1")
print(f"key是否存在: {is_exist}")

# ====================== 测试4：删除缓存 ======================
delete_success = RedisCacheUtil.delete_cache(redis_client, "product:detail:1")
print(f"删除缓存结果: {delete_success}")

# 再次读取，应该返回None
cache_data_after_delete = RedisCacheUtil.get_cache(redis_client, "product:detail:1")
print(f"删除后读取缓存: {cache_data_after_delete}")