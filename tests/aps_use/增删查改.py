# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/25
# @File : 增删查改.py

# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/25
# @File : apscheduler_baseuse.py
import datetime
import time

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

local_timezone = pytz.timezone('Asia/Shanghai')
scheduler = BackgroundScheduler(timezone=local_timezone)


def my_task1(name):
    print(f"间隔任务 {datetime.datetime.now()}---{name}")


def my_task2(name):
    print(f"定时任务 {datetime.datetime.now()}---{name}")


def my_task3(name):
    print(f"周期任务 {datetime.datetime.now()}---{name}")


# 添加任务，设置为每隔 110 秒执行一次
scheduler.add_job(my_task1,
                  id='interval_task',
                  trigger=IntervalTrigger(seconds=3),
                  args=['间隔任务'])

# 设置定时任务，2024年8月6号2点执行
scheduler.add_job(my_task2,
                  id='date_task',
                  trigger=DateTrigger(run_date='2024-11-25 17:30:00', timezone=local_timezone),
                  args=['定时任务'])

# 添加周期任务，设置每个小时的第5分钟，30秒执行
scheduler.add_job(my_task3, id='cron_task',
                  trigger=CronTrigger(year='*', month='*', day='*', hour='*', minute='*', second='30'),
                  args=['corn周期任务'],
                  timezone=local_timezone)

# 启动调度器
scheduler.start()

jobs = scheduler.get_jobs()
for job in jobs:
    print(f"Job id: {job.id}, next run time: {job.next_run_time}")

time.sleep(5)
# 暂停任务
scheduler.pause_job('interval_task')

time.sleep(5)
# 恢复任务
scheduler.resume_job('interval_task')

time.sleep(5)
# 删除任务
scheduler.remove_job('interval_task')

# 保持主线程运行，以便调度器可以继续运行
while True:
    time.sleep(2)
