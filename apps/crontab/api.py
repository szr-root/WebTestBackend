# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/25
# @File : api.py

import datetime
import time
import pytz
from common.settings import REDIS_CONFIG
from fastapi import APIRouter, HTTPException
from .schemas import CornJobFrom
from .models import CornJob
from apps.testplan.models import Tasks
from apps.projects.models import TestEnv, TestProject
from tortoise import transactions
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore

# ==========================APS配置 ==========================

local_timezone = pytz.timezone('Asia/Shanghai')

# 配置 APScheduler
jobstores = {
    'default': RedisJobStore(host=REDIS_CONFIG.get('host'),
                             port=REDIS_CONFIG.get('port'),
                             db=REDIS_CONFIG.get('db'),
                             password=REDIS_CONFIG.get('password'))
}
# 设置最大的执行线程数
executors = {
    'default': ThreadPoolExecutor(20)
}
# 设置最大的任务数
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
# 创建一个调度器
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                timezone='Asia/Shanghai')

scheduler.start()

# ==========================APS ==========================
router = APIRouter(prefix='/api/cron')


def run_test_task(task_id, env_id):
    pass


# 创建定时任务
@router.post('/crontab', tags=['定时任务'], summary="创建定时任务", status_code=201)
async def create_crontab(item: CornJobFrom):
    corn_task_id = str(int(time.time() * 1000))

    task = Tasks.get_or_none(id=item.task)
    if not task:
        raise HTTPException(status_code=422, detail='创建失败,测试任务不存在')

    env = TestEnv.get_or_none(id=item.env)
    if not env:
        raise HTTPException(status_code=422, detail='创建失败,执行环境不存在')

    project = TestProject.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail='创建失败,所属项目不存在')

    if item.run_type not in ['Interval', 'date', 'crontab']:
        raise HTTPException(status_code=422, detail='创建失败,任务类型错误')

    date = datetime.datetime.strptime(item.date, '%Y-%m-%d %H:%M:%S')
    if date < datetime.datetime.now() and item.run_type == 'date':
        raise HTTPException(status_code=422, detail='创建失败,执行时间不能小于当前时间')

    # 添加事务
    async with transactions.in_transaction('cron') as cron_tran:
        try:
            if item.run_type == 'Interval':
                trigger = IntervalTrigger(item.interval, timezone=local_timezone)
            elif item.run_type == 'date':
                trigger = DateTrigger(run_date=date, timezone=local_timezone)
            else:
                trigger = CronTrigger(**item.crontab.dict(), timezone=local_timezone)

            job = scheduler.add_job(
                func=run_test_task,
                trigger=trigger,
                id=corn_task_id,
                name=item.name,
                kwargs={"task_id": item.task, "env_id": item.env}
            )
            corn = await CornJob.create(id=corn_task_id, name=item.name, project=item.project, task=item.task,
                                        env=item.env, run_type=item.run_type, interval=item.interval,
                                        date=item.date, crontab=item.crontab, state=item.state)
        except Exception as e:
            # 事务回滚
            await cron_tran.rollback()
            # 取消定时任务
            scheduler.remove_job(corn_task_id)
            raise HTTPException(status_code=422, detail='创建失败')
        else:
            await cron_tran.commit()
            return corn
