"""
RabbitMQ队列配置脚本
用于设置死信队列和订单队列
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rabbitmq import rabbitmq_manager


def setup_dead_letter_queue():
    """
    配置死信队列
    1. 声明死信交换机
    2. 声明订单队列，设置TTL和死信交换机
    3. 声明死信队列，用于接收过期的订单消息
    """
    print("Setting up dead letter queue...")
    
    # 死信交换机名称
    dead_letter_exchange = "order_dead_letter_exchange"
    
    # 订单队列名称
    order_queue = "seckill_orders"
    
    # 死信队列名称
    dead_letter_queue = "seckill_orders_dead_letter"
    
    # 死信路由键
    dead_letter_routing_key = "order_expired"
    
    # 订单超时时间（30分钟，单位：毫秒）
    order_ttl = 30 * 60 * 1000
    
    try:
        # 声明死信交换机
        rabbitmq_manager.declare_exchange(dead_letter_exchange)
        
        # 声明死信队列
        rabbitmq_manager.declare_queue(dead_letter_queue, durable=True)
        
        # 绑定死信队列到死信交换机
        rabbitmq_manager.bind_queue(dead_letter_queue, dead_letter_exchange, dead_letter_routing_key)
        
        # 声明订单队列，设置TTL和死信交换机
        rabbitmq_manager.declare_queue(
            order_queue,
            durable=True,
            ttl=order_ttl,
            dead_letter_exchange=dead_letter_exchange,
            dead_letter_routing_key=dead_letter_routing_key
        )
        
        print("Dead letter queue setup completed successfully!")
        print(f"Order queue: {order_queue} (TTL: {order_ttl}ms)")
        print(f"Dead letter exchange: {dead_letter_exchange}")
        print(f"Dead letter queue: {dead_letter_queue}")
    except Exception as e:
        print(f"Failed to setup dead letter queue: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭连接
        rabbitmq_manager.close()


if __name__ == "__main__":
    setup_dead_letter_queue()
