from app.core.bloom_filter import BloomFilter

# 测试布隆过滤器
print("测试布隆过滤器...")

# 初始化布隆过滤器
bf = BloomFilter(size=1000, hash_count=3)

# 添加一些元素
test_items = ["1", "2", "3", "4", "5"]
for item in test_items:
    bf.add(item)
    print(f"添加元素: {item}")

# 测试存在的元素
print("\n测试存在的元素:")
for item in test_items:
    result = bf.contains(item)
    print(f"元素 {item} 是否存在: {result}")

# 测试不存在的元素
print("\n测试不存在的元素:")
non_existent_items = ["6", "7", "8", "9", "10"]
for item in non_existent_items:
    result = bf.contains(item)
    print(f"元素 {item} 是否存在: {result}")

# 测试批量添加
print("\n测试批量添加:")
bf2 = BloomFilter(size=1000, hash_count=3)
batch_items = {"11", "12", "13", "14", "15"}
bf2.add_batch(batch_items)
for item in batch_items:
    result = bf2.contains(item)
    print(f"批量添加的元素 {item} 是否存在: {result}")

print("\n布隆过滤器测试完成！")
