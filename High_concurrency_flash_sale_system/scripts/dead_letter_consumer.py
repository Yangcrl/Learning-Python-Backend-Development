"""
死信消费者脚本
用于消费死信队列中的消息，取消超时订单并回滚Redis库存
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rabbitmq import rabbitmq_manager
from app.core.database import SessionLocal
from app.models import Order
from app.core.redis_client import get_redis_client


def rollback_stock(redis_client, activity_id, quantity=1):
    """
    回滚Redis库存
    
    Args:
        redis_client: Redis客户端
        activity_id: 活动ID
        quantity: 回滚数量
    """
    stock_key = f"seckill:stock:{activity_id}"
    try:
        # 增加库存
        redis_client.incrby(stock_key, quantity)
        print(f"Stock rolled back for activity {activity_id}: +{quantity}")
        return True
    except Exception as e:
        print(f"Failed to rollback stock: {e}")
        return False


def cancel_order(db, order_id):
    """
    取消订单
    
    Args:
        db: 数据库会话
        order_id: 订单ID
    """
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            if order.status == "pending":
                order.status = "cancelled"
                db.commit()
                print(f"Order {order_id} cancelled successfully")
                return True
            else:
                print(f"Order {order_id} already {order.status}, cannot cancel")
                return False
        else:
            print(f"Order {order_id} not found")
            return False
    except Exception as e:
        db.rollback()
        print(f"Failed to cancel order: {e}")
        return False


def dead_letter_callback(ch, method, properties, body):
    """
    死信消息处理回调函数
    
    Args:
        ch: 通道
        method: 方法
        properties: 属性
        body: 消息体
    """
    try:
        # 解析消息
        order_data = json.loads(body)
        print(f"Received dead letter message: {order_data}")
        
        # 获取订单信息
        order_id = order_data.get("order_id")
        activity_id = order_data.get("activity_id")
        quantity = order_data.get("quantity", 1)
        
        if not order_id or not activity_id:
            print("Invalid order data, missing order_id or activity_id")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # 创建数据库会话
        db = SessionLocal()
        redis_client = get_redis_client()
        
        try:
            # 取消订单
            cancel_success = cancel_order(db, order_id)
            
            # 回滚库存
            if cancel_success:
                rollback_stock(redis_client, activity_id, quantity)
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Dead letter message processed successfully: {order_id}")
        finally:
            db.close()
    except Exception as e:
        print(f"Error processing dead letter message: {e}")
        import traceback
        traceback.print_exc()
        # 确认消息，避免消息一直重试
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_dead_letter_consumer():
    """
    启动死信消费者
    """
    print("Starting dead letter consumer...")
    try:
        # 开始消费消息
        rabbitmq_manager.consume_messages(
            queue_name="seckill_orders_dead_letter",
            callback=dead_letter_callback
        )
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        # 关闭连接
        rabbitmq_manager.close()


if __name__ == "__main__":
    start_dead_letter_consumer()
