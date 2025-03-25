# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/25
# @File : api.py
import asyncio
import datetime
import time
import pytz

from common.rabbitmq_producer import mq
from common.settings import REDIS_CONFIG
from fastapi import APIRouter, HTTPException
from .schemas import CornJobFrom, UpdagteCornJobFrom
from .models import CornJob
from apps.testplan.models import Tasks
from apps.projects.models import TestEnv, TestProject
from tortoise import transactions
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore

# ==========================APS配置 ==========================
from ..runner.models import TaskRunRecords, SuiteRunRecords, CaseRunRecords
from ..testmanage.models import Suite

local_timezone = pytz.timezone('Asia/Shanghai')

# 配置 APScheduler
jobstores = {
    'default': RedisJobStore(host=REDIS_CONFIG.get('host'),
                             port=REDIS_CONFIG.get('port'),
                             db=REDIS_CONFIG.get('db'),
                             password=REDIS_CONFIG.get('password'))
}
# 设置最大的执行线程数 （使用异步，不用线程）
# executors = {
#     'default': ThreadPoolExecutor(20)
# }
# 设置最大的任务数
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
# 创建一个调度器
# scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
#                                 timezone='Asia/Shanghai')

scheduler = AsyncIOScheduler(jobstores=jobstores, job_defaults=job_defaults,
                             timezone='Asia/Shanghai')

scheduler.start()

# ==========================APS ==========================
router = APIRouter(prefix='/api/cron')


async def run_test_task(task_id, env_id):
    """执行定时任务"""
    async with transactions.in_transaction():
        task = await Tasks.get_or_none(id=task_id).prefetch_related('suite', 'project')
        env = await TestEnv.get_or_none(id=env_id)
        env_config = {
            "is_debug": False,
            "browser_type": 'chromium',
            "host": env.host,
            "global_variable": env.global_vars
        }
        # 创建一条任务执行的记录
        task_record = await TaskRunRecords.create(task=task, env=env_config, project=task.project)
        task_count = 0
        for suite in await task.suite.all():
            cases = []
            suite_ = await Suite.get_or_none(id=suite.id).prefetch_related('cases')
            suite_record = await SuiteRunRecords.create(suite=suite_, env=env_config, task_run_records=task_record)
            for i in await suite_.cases.all().order_by("sort"):
                case_ = await i.cases
                case_record = await CaseRunRecords.create(case=case_, suite_run_records=suite_record)
                cases.append({
                    "record_id": case_record.id,
                    'id': case_.id,
                    'name': case_.name,
                    'skip': i.skip,
                    'steps': case_.steps
                })
            task_count += len(cases)
            suite_record.all = len(cases)
            await suite_record.save()
            run_suite = {
                'id': suite_.id,
                "suite_record_id": suite_record.id,
                "task_record_id": task_record.id,
                'name': suite_.name,
                'setup_step': suite_.suite_setup_step,
                'cases': cases
            }
            mq.send_test_task(env_config, run_suite)

        # 修改任务中的用例总数
        task_record.all = task_count
        await task_record.save()
    print("任务执行提交", task_id, env_id)

    # print("执行了", task_id, env_id)


# 创建定时任务
@router.post('/crontab/', tags=['定时任务'], summary="创建定时任务", status_code=201)
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
    async with transactions.in_transaction('default') as cron_tran:
        try:
            if item.run_type == 'Interval':
                trigger = IntervalTrigger(seconds=item.interval, timezone=local_timezone)
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
            print('job_time:', corn_task_id)
            item.date = date.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
            corn = await CornJob.create(id=corn_task_id, name=item.name, project_id=item.project, task_id=item.task,
                                        env_id=item.env, run_type=item.run_type, interval=item.interval,
                                        date=item.date, crontab=item.crontab.dict(), state=item.state)
        except Exception as e:
            # 事务回滚
            await cron_tran.rollback()
            # 取消定时任务
            scheduler.remove_job(corn_task_id)
            raise HTTPException(status_code=422, detail=f'创建失败,{e}')
        else:
            await cron_tran.commit()
            return corn


# 获取定时任务列表
@router.get('/crontab', tags=['定时任务'], summary="获取定时任务列表")
async def get_crontab_list(project: int):
    crons = await CornJob.filter(project_id=project).all().prefetch_related('env', 'task')

    return [{
        "id": cron.id,
        "name": cron.name,
        "create_time": cron.create_time,
        "task_id": cron.task.id,
        "task_name": cron.task.name if cron.task else None,
        "env_id": cron.env.id,
        "env_name": cron.env.name if cron.env else None,
        "run_type": cron.run_type,
        "interval": cron.interval,
        "date": cron.date,
        "crontab": cron.crontab,
        "state": cron.state,
    } for cron in crons]


# todo 感觉有bug，有时修改定时任务时，没有修改成功，，也可能是redis没有该条数据的原因，后续可能需要排查
@router.patch('/crontab/{id}', tags=['定时任务'], summary="暂停/恢复定时任务")
async def update_crontab(id: str):
    corn = await CornJob.get_or_none(id=id)
    if not corn:
        raise HTTPException(status_code=422, detail='定时任务不存在')
    if scheduler.get_job(id):
        scheduler.pause_job(id)
    async with transactions.in_transaction() as cron_tran:
        try:
            corn.state = not corn.state
            # 判断是启用还是暂停
            if corn.state:
                scheduler.resume_job(id)
            else:
                scheduler.pause_job(id)
            await corn.save()
        except Exception as e:
            await cron_tran.rollback()
            raise HTTPException(status_code=422, detail=f'操作失败:{e}')
        else:
            await cron_tran.commit()
        return corn


# 删除定时任务
@router.delete('/crontab/{id}', tags=['定时任务'], summary="删除定时任务", status_code=204)
async def delete_crontab(id: str):
    corn = await CornJob.get_or_none(id=id)
    if not corn:
        raise HTTPException(status_code=422, detail='定时任务不存在')
    if scheduler.get_job(id):
        scheduler.remove_job(id)
    await corn.delete()


# 修改定时任务配置
@router.put('/crontab/{id}', tags=['定时任务'], summary="修改定时任务配置")
async def update_job(id: str, item: UpdagteCornJobFrom):
    corn = await CornJob.get_or_none(id=id)
    if not corn:
        raise HTTPException(status_code=422, detail='定时任务不存在')

    if item.run_type not in ['Interval', 'date', 'crontab']:
        raise HTTPException(status_code=422, detail='创建失败,任务类型错误')

    date = datetime.datetime.strptime(item.date, '%Y-%m-%d %H:%M:%S')
    if date < datetime.datetime.now() and item.run_type == 'date':
        raise HTTPException(status_code=422, detail='创建失败,执行时间不能小于当前时间')
    try:
        if corn.run_type == 'Interval':
            trigger = IntervalTrigger(seconds=item.interval, timezone=local_timezone)
        elif corn.run_type == 'date':
            trigger = DateTrigger(run_date=item.date, timezone=local_timezone)
        else:
            trigger = CronTrigger(**item.crontab.dict(), timezone=local_timezone)

        scheduler.modify_job(id, trigger=trigger)
        # 将时间转成utc时间存到数据，数据库保存时utc
        item.date = date.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        await corn.update_from_dict(item.dict(exclude_unset=True)).save()

    except Exception as e:
        raise HTTPException(status_code=422, detail=f'修改失败:{e}')

    return corn
