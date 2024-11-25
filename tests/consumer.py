# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/20
# @File : consumer.py
#
# import pika
#
#
# def callback(ch, method, properties, body):
#     print(f" [x] Received {body}")
#
#
# # 创建连接
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='113.45.179.110', port=5672))
# channel = connection.channel()
#
# # 设置回调函数，处理接收到的消息
# channel.basic_consume(queue='test', on_message_callback=callback, auto_ack=True)
#
# print(' [*] Waiting for messages. To exit press CTRL+C')
#
# # 开始消费消息
# channel.start_consuming()
#
