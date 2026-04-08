"""
这是 models 包的索引文件，
通过相对导入集中了所有模型类，
并定义了公开接口，让其他文件导入模型时路径更短、代码更整洁
"""

# 从当前目录下的 user.py 文件导入 User 类
from .user import User
# 从当前目录下的 product.py 文件导入 Product 类
from .product import Product
# 从当前目录下的 seckill_activity.py 文件导入 SeckillActivity 类
from .seckill_activity import SeckillActivity
# 从当前目录下的 order.py 文件导入 Order 类
from .order import Order

# 定义公开接口
__all__ = ['User', 'Product', 'SeckillActivity', 'Order']