# 高并发秒杀系统

## 项目简介

这是一个基于FastAPI和Redis构建的高并发秒杀系统，实现了商品秒杀的核心功能，包括库存预热、分布式锁、接口限流等特性，能够应对高并发场景下的秒杀请求。

## 技术栈

- **后端框架**：FastAPI
- **数据库**：MySQL + SQLAlchemy ORM
- **缓存**：Redis
- **认证**：JWT
- **性能优化**：
  - Redis缓存
  - Lua脚本原子操作
  - 分布式锁
  - 布隆过滤器
  - 数据库连接池
  - 接口限流

## 核心功能

1. **用户管理**：注册、登录、JWT认证
2. **商品管理**：商品列表、商品详情（带缓存）
3. **秒杀管理**：
   - 秒杀活动创建
   - 库存预热
   - 秒杀接口（同步/异步）
   - 分布式锁防止超卖
   - 接口限流
4. **缓存管理**：
   - 商品详情缓存
   - 秒杀库存缓存
   - 布隆过滤器防止缓存穿透

## 项目结构

```
High_concurrency_flash_sale_system/
├── app/                # 主应用代码
│   ├── api/            # API接口
│   │   ├── auth.py     # 认证接口
│   │   ├── product.py  # 商品接口
│   │   └── seckill.py  # 秒杀接口
│   ├── core/           # 核心功能
│   │   ├── config.py   # 配置管理
│   │   ├── database.py # 数据库连接
│   │   ├── redis_client.py # Redis客户端
│   │   ├── security.py # 安全相关
│   │   ├── bloom_filter.py # 布隆过滤器
│   │   ├── redis_lock.py # 分布式锁
│   │   ├── rate_limiter.py # 限流
│   │   └── middleware.py # 中间件
│   ├── models/         # 数据模型
│   │   ├── user.py     # 用户模型
│   │   ├── product.py  # 商品模型
│   │   └── seckill_activity.py # 秒杀活动模型
│   ├── schemas/        # 数据校验
│   │   ├── user.py     # 用户相关
│   │   └── product.py  # 商品相关
│   ├── services/       # 业务逻辑
│   │   └── product_service.py # 商品服务
│   └── main.py         # 应用入口
├── lua/                # Lua脚本
│   └── stock.lua       # 库存扣减脚本
├── scripts/            # 辅助脚本
│   ├── prepare_data.py # 数据准备
│   ├── preheat.py      # 库存预热
│   └── warm_cache.py   # 缓存预热
├── tests/              # 测试文件
│   ├── test_api.py     # API测试
│   ├── test_seckill.py # 秒杀测试
│   └── test_redis_lock.py # 分布式锁测试
├── alembic/            # 数据库迁移
├── requirements.txt    # 依赖管理
└── README.md           # 项目文档
```

## 快速开始

### 1. 环境准备

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置文件

创建 `.env` 文件，配置数据库和Redis连接信息：

```
# .env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/seckill
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

### 4. 数据库初始化

```bash
# 生成迁移文件
alembic revision --autogenerate -m "init tables"

# 执行迁移
alembic upgrade head
```

### 5. 数据准备

```bash
python scripts/prepare_data.py
```

### 6. 库存预热

```bash
python scripts/preheat.py
```

### 7. 启动服务

```bash
uvicorn app.main:app --reload
```

服务将在 `http://127.0.0.1:8000` 启动。

## API文档

启动服务后，可以访问以下地址查看API文档：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 核心技术点

### 1. 秒杀库存预热

- 将秒杀活动的库存提前加载到Redis中
- 使用hash结构存储库存信息
- 设置合理的过期时间

### 2. 分布式锁

- 使用Redis的setnx命令实现
- 支持设置过期时间，防止死锁
- 使用Lua脚本确保原子释放锁

### 3. 库存扣减

- 使用Lua脚本实现原子扣减库存
- 防止超卖
- 确保库存数据的一致性

### 4. 缓存优化

- 商品详情缓存
- 布隆过滤器防止缓存穿透
- 缓存预热

### 5. 接口限流

- 基于Redis的滑动窗口限流
- 限制同一用户的请求频率
- 防止恶意请求

## 压测结果

### 无缓存压测
- QPS: ~480
- 平均响应时间: ~21ms
- 成功率: 99.8%

### 有缓存压测
- QPS: ~1450
- 平均响应时间: ~6ms
- 成功率: 99.99%

## 项目亮点

1. **高并发支持**：通过Redis缓存和Lua脚本，支持高并发秒杀
2. **数据一致性**：使用分布式锁和原子操作，确保库存数据的一致性
3. **性能优化**：多级缓存、连接池优化、限流等措施，提高系统性能
4. **安全性**：JWT认证、接口限流、防缓存穿透等安全措施
5. **可扩展性**：模块化设计，易于扩展和维护

## 后续优化方向

1. **异步改造**：使用aioredis和异步IO，进一步提高并发能力
2. **分布式部署**：支持多实例部署，提高系统可用性
3. **监控告警**：添加系统监控和告警机制
4. **降级方案**：实现服务降级策略，提高系统稳定性
5. **容器化**：使用Docker容器化部署，简化运维

## 许可证

MIT License
