"""
RabbitMQ连接测试脚本
"""

import pika

print("Testing RabbitMQ connection...")

try:
    # 尝试连接RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')
        )
    )
    print("Successfully connected to RabbitMQ!")
    connection.close()
except Exception as e:
    print(f"Failed to connect to RabbitMQ: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
