# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/20
# @File : mq_case_run_demo.py
import json
import pika
from webtestengine.core.runner import Runner

from common.settings import MQ_CONFIG


class MQConsumer:
    def __init__(self):
        # 连接到rabbitmq服务器
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=MQ_CONFIG.get('host'), port=MQ_CONFIG.get('port'))
        )
        self.channel = self.connection.channel()

        # 设置回调函数，处理接收到的消息
        self.channel.basic_consume(queue=MQ_CONFIG.get('queue'), on_message_callback=self.run_test, auto_ack=True)

    def run_test(self, channel, method, properties, body):
        datas = json.loads(body.decode())
        env_config = datas.get('env_config')
        run_suite = datas.get('run_suite')
        runner = Runner(env_config, run_suite)
        runner.run()

    def main(self):
        # 启动执行，等待任务
        self.channel.start_consuming()


if __name__ == '__main__':
    c1 = MQConsumer()
    c1.main()
