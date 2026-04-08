"""
RabbitMQ连接管理模块
"""

import pika
import json
from typing import Optional, Callable


class RabbitMQManager:
    """
    RabbitMQ连接管理类
    """
    
    def __init__(self, host: str = 'localhost', port: int = 5672, 
                 username: str = 'guest', password: str = 'guest',
                 virtual_host: str = '/'):
        """
        初始化RabbitMQ连接
        
        Args:
            host: RabbitMQ主机地址
            port: RabbitMQ端口
            username: RabbitMQ用户名
            password: RabbitMQ密码
            virtual_host: RabbitMQ虚拟主机
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.connection = None
        self.channel = None
    
    def connect(self):
        """
        建立RabbitMQ连接
        """
        print(f"Attempting to connect to RabbitMQ at {self.host}:{self.port}...")
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            print(f"Successfully connected to RabbitMQ at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            import traceback
            traceback.print_exc()
    
    def close(self):
        """
        关闭RabbitMQ连接
        """
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        print("RabbitMQ connection closed")
    
    def declare_exchange(self, exchange_name: str, exchange_type: str = 'direct', durable: bool = True):
        """
        声明交换机
        
        Args:
            exchange_name: 交换机名称
            exchange_type: 交换机类型（direct, fanout, topic, headers）
            durable: 是否持久化交换机
        """
        if not self.channel:
            self.connect()
        
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable
        )
        print(f"Exchange {exchange_name} declared")
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        """
        绑定队列到交换机
        
        Args:
            queue_name: 队列名称
            exchange_name: 交换机名称
            routing_key: 路由键
        """
        if not self.channel:
            self.connect()
        
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        print(f"Queue {queue_name} bound to exchange {exchange_name} with routing key {routing_key}")
    
    def declare_queue(self, queue_name: str, durable: bool = True, 
                     ttl: int = None, dead_letter_exchange: str = None,
                     dead_letter_routing_key: str = None):
        """
        声明队列
        
        Args:
            queue_name: 队列名称
            durable: 是否持久化队列
            ttl: 消息过期时间（毫秒）
            dead_letter_exchange: 死信交换机名称
            dead_letter_routing_key: 死信路由键
        """
        if not self.channel:
            self.connect()
        
        arguments = {}
        if ttl:
            arguments['x-message-ttl'] = ttl
        if dead_letter_exchange:
            arguments['x-dead-letter-exchange'] = dead_letter_exchange
        if dead_letter_routing_key:
            arguments['x-dead-letter-routing-key'] = dead_letter_routing_key
        
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            arguments=arguments
        )
        print(f"Queue {queue_name} declared with arguments: {arguments}")
    
    def publish_message(self, queue_name: str, message: dict, exchange: str = ''):
        """
        发布消息到队列
        
        Args:
            queue_name: 队列名称
            message: 消息内容
            exchange: 交换机名称
        """
        if not self.channel:
            self.connect()
        
        # 确保队列存在
        self.declare_queue(queue_name)
        
        # 发送消息
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 持久化消息
            )
        )
        print(f"Message published to queue {queue_name}: {message}")
    
    def consume_messages(self, queue_name: str, callback: Callable):
        """
        消费队列消息
        
        Args:
            queue_name: 队列名称
            callback: 消息处理回调函数
        """
        if not self.channel:
            self.connect()
        
        # 确保队列存在
        self.declare_queue(queue_name)
        
        # 设置手动确认
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        print(f"Waiting for messages in queue {queue_name}...")
        self.channel.start_consuming()


# 创建RabbitMQ管理器实例
rabbitmq_manager = RabbitMQManager()
