# 导入 Redis 官方 Python 客户端库，用于连接、操作 Redis 数据库
import redis
# 导入 Redis 连接池类，实现连接复用，提升性能，避免频繁创建/销毁连接
from redis.connection import ConnectionPool
# 导入类型注解工具：Optional（变量可为指定类型/None）、Generator（生成器类型），用于规范代码类型
from typing import Optional, Generator
# 导入 JSON 模块，用于 Python 数据 ↔ Redis 可存储的字符串 相互转换（序列化/反序列化）
import json
# 导入操作系统交互模块
import os

# 尝试导入环境变量加载工具，如果不存在则使用默认值
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found, using default values")

"""redis配置"""
# redis 服务地址
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
# redis 端口
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# redis 密码
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "123456")
# reids 数据库编号，默认0
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
# 连接池最大连接数
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))
# 连接超时时间，单位秒
REDIS_CONNECT_TIMEOUT = int(os.getenv("REDIS_CONNECT_TIMEOUT", "8"))
# 读写超时时间，单位秒
REDIS_READ_TIMEOUT = int(os.getenv("REDIS_READ_TIMEOUT", "8"))

"""全局单例连接池初始化"""
pool = ConnectionPool(
    host = REDIS_HOST,
    port = REDIS_PORT,
    password = REDIS_PASSWORD,
    db = REDIS_DB,
    max_connections = REDIS_MAX_CONNECTIONS,
    socket_connect_timeout = REDIS_CONNECT_TIMEOUT,
    socket_timeout = REDIS_READ_TIMEOUT,  # 使用socket_timeout代替read_timeout
    health_check_interval = 30, # 30秒健康检查一次，断开的连接自动重连
)

"""fastapi 依赖注入：获取redis 连接"""
def get_redis_client() -> Generator[redis.Redis, None, None]:
    """
    fastapi 接口依赖注入用，自动从连接池获取连接，用完自动归还
    用法：在接口参数里写 redis_client: Redis = Depends(get_redis_client)
    """
    # 从连接池获取一个连接
    client = redis.Redis(connection_pool = pool, decode_responses = True)
    try:
        # 测试连接是否正常
        client.ping()
        yield client
    except Exception as e:
        print(f"Redis 连接异常：{str(e)}")
        raise e
    finally:
        # 注意：这里不需要close(), 连接会自动归还到连接池
        # redis-py 的连接池会自动管理连接的生命周期
        pass

"""redis 缓存工具类"""
class RedisCacheUtil:
    """
    封装秒杀项目常用的缓存操作，自动处理JSON序列化/反序列化
    避免每个业务都重复写序列化代码，统一异常处理
    """

    @staticmethod
    def set_cache(
            client: redis.Redis,
            key: str,
            value: any,
            expire: Optional[int] = 600,  # 默认缓存10分钟
            nx: bool = False              # nx = True 表示key不存在时才设置缓存(分布式锁用)
    ) -> bool:
        """
        写入缓存，自动将Python 对象序列化为JSON字符串
        :param client: Redis 连接对象
        :param key: 缓存键，命名规范：业务:模块:唯一标识 例：product:detail:1
        :param value:要缓存的Python 对象（字典、列表、模型对象等）
        :param expire:过期时间，单位秒，None 表示永不过期
        :param nx:是否仅当key 不存在时写入
        :return:成功返回True，失败返回False
        """
        try:
            # 将Python 对象转为JSON 字符串，ensure_ascii=False 支持中文
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            # 写入Redis
            client.set(key, json_value, ex=expire, nx=nx)
            return True
        except Exception as e:
            print(f"Redis 写入缓存异常：key={key}, 错误={str(e)}")
            return False

    @staticmethod
    def get_cache(
            client: redis.Redis,
            key: str
    ) -> Optional[any]:
        """
        获取缓存，自动将JSON字符串反序列化为Python对象
        :param client: Redis 连接对象
        :param key: 缓存键
        :return: 缓存值，不存在返回None
        """
        try:
            json_value = client.get(key)
            # 如果缓存值不存在，返回None
            if json_value is None:
                return None
            # 将JSON字符串转为Python对象
            return json.loads(json_value)
        except Exception as e:
            print(f"Redis 读取缓存异常：key={key}, 错误={str(e)}")
            return None

    @staticmethod
    def delete_cache(
            client: redis.Redis,
            key: str
    ) -> bool:
        """
        删除缓存
        :param client: Redis 连接对象
        :param key: 缓存键
        :return: 成功返回True，失败返回False
        """
        try:
            client.delete(key)
            return True
        except Exception as e:
            print(f"Redis 删除缓存异常：key={key}, 错误={str(e)}")
            return False

    @staticmethod
    def is_exist(
            client: redis.Redis,
            key: str
    ) -> bool:
        """
        检查key 是否存在，防止缓存穿透
        :param client: Redis 连接对象
        :param key: 缓存键
        :return: 存在返回True，不存在返回False
        """
        try:
            return client.exists(key) > 0
        except Exception as e:
            print(f"Redis 检查key异常：key={key}, 错误={str(e)}")
            return False