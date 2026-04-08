"""
订单超时取消测试脚本
用于测试死信队列和订单超时取消功能
"""

import json
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rabbitmq import rabbitmq_manager
from app.core.database import SessionLocal
from app.models import Order
from app.core.redis_client import get_redis_client


def test_order_timeout():
    """
    测试订单超时取消功能
    1. 向订单队列发送一个测试订单
    2. 等待消息过期
    3. 检查订单是否被取消
    4. 检查库存是否被回滚
    """
    print("Testing order timeout cancellation...")
    
    # 测试活动ID
    activity_id = 1
    
    # 生成订单ID
    import uuid
    order_id = str(uuid.uuid4())
    
    # 构建测试订单消息
    order_message = {
        "order_id": order_id,
        "activity_id": activity_id,
        "product_id": 1,
        "user_id": 1,
        "quantity": 1,
        "amount": 99.99,
        "created_at": time.time()
    }
    
    # 获取Redis客户端
    redis_client = get_redis_client()
    
    # 保存初始库存
    stock_key = f"seckill:stock:{activity_id}"
    initial_stock = redis_client.get(stock_key)
    print(f"Initial stock for activity {activity_id}: {initial_stock}")
    
    # 发送订单消息到队列
    try:
        rabbitmq_manager.publish_message(
            queue_name="seckill_orders",
            message=order_message
        )
        print(f"Test order sent: {order_id}")
    except Exception as e:
        print(f"Failed to send test order: {e}")
        return
    
    # 等待消息过期（使用较短的时间进行测试）
    print("Waiting for order to expire...")
    # 这里使用10秒作为测试超时时间
    time.sleep(10)
    
    # 检查订单状态
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            print(f"Order status: {order.status}")
            if order.status == "cancelled":
                print("✓ Order cancelled successfully")
            else:
                print("✗ Order not cancelled")
        else:
            print("✗ Order not found")
        
        # 检查库存是否回滚
        current_stock = redis_client.get(stock_key)
        print(f"Current stock for activity {activity_id}: {current_stock}")
        if current_stock == initial_stock:
            print("✓ Stock rolled back successfully")
        else:
            print("✗ Stock not rolled back")
    finally:
        db.close()
    
    # 关闭连接
    rabbitmq_manager.close()


if __name__ == "__main__":
    test_order_timeout()
