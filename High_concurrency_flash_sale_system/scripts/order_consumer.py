"""
订单消费者脚本
用于消费RabbitMQ队列中的秒杀订单消息并创建订单
"""

import json
import pika
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rabbitmq import rabbitmq_manager
from app.core.database import SessionLocal
from app.models import Order


def create_order(db, order_data):
    """
    创建订单
    
    Args:
        db: 数据库会话
        order_data: 订单数据
    """
    try:
        # 创建订单
        order = Order(
            id=order_data["order_id"],
            user_id=order_data["user_id"],
            product_id=order_data["product_id"],
            quantity=order_data["quantity"],
            total_amount=order_data["amount"],
            status="pending"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        print(f"Order created successfully: {order_data['order_id']}")
        return True
    except Exception as e:
        db.rollback()
        print(f"Failed to create order: {e}")
        return False


def order_callback(ch, method, properties, body):
    """
    订单消息处理回调函数
    
    Args:
        ch: 通道
        method: 方法
        properties: 属性
        body: 消息体
    """
    try:
        # 解析消息
        order_data = json.loads(body)
        print(f"Received order message: {order_data}")
        
        # 创建数据库会话
        db = SessionLocal()
        try:
            # 创建订单
            success = create_order(db, order_data)
            if success:
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(f"Order message processed successfully: {order_data['order_id']}")
            else:
                # 拒绝消息，重新入队
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                print(f"Order message processing failed, requeuing: {order_data['order_id']}")
        finally:
            db.close()
    except Exception as e:
        print(f"Error processing order message: {e}")
        # 拒绝消息，重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """
    启动订单消费者
    """
    print("Starting order consumer...")
    try:
        # 开始消费消息
        rabbitmq_manager.consume_messages(
            queue_name="seckill_orders",
            callback=order_callback
        )
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        # 关闭连接
        rabbitmq_manager.close()


if __name__ == "__main__":
    start_consumer()
