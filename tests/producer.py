# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/20
# @File : producer.py
import time

import pika

# 连接到rabbitmq服务器
connection = pika.BlockingConnection(pika.ConnectionParameters(host='113.45.179.110', port=5672))
channel = connection.channel()

# 声明一个队列
channel.queue_declare(queue='test')

# 发送消息
for i in range(10):
    time.sleep(5)
    channel.basic_publish(exchange='', routing_key='test', body=b'test message')

print(" [x] Sent 'Hello, RabbitMQ!'")

# 关闭连接
connection.close()
