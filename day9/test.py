import redis

# 连接免费的在线Redis测试服务
r = redis.Redis(
    host='redis-13919.c295.ap-southeast-1-1.ec2.redns.redis-cloud.com',
    port=13919,
    password='xQd8Kz9Lw2eR5tY7uI3oP0aS4dF6gHj',
    db=0,
    decode_responses=True
)

# 测试Redis的读写功能
r.set('my_test', 'Redis功能测试成功！')
print("运行结果：", r.get('my_test'))