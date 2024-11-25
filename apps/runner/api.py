# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/12
# @File : api.py
from typing import Annotated, List

from fastapi import APIRouter, HTTPException

from apps.projects.models import TestEnv
from apps.runner.schemas import RunForm, SuiteInfoSchemas, TaskResultsSchemas
from apps.testmanage.models import Cases, Suite
from apps.testplan.models import Tasks
from common.rabbitmq_producer import mq
from .models import TaskRunRecords, SuiteRunRecords, CaseRunRecords
from tortoise.transactions import in_transaction

# 创建路由对象
router = APIRouter(prefix='/api/run')


# 执行单条用例
@router.post('/cases/{id}', tags=['测试运行'], summary='执行用例')
async def run_cases(id: int, item: RunForm):
    # 创建事务，会自动提交或者回滚
    async with in_transaction():
        # 获取用例数据
        case_ = await Cases.get_or_none(id=id)
        if not case_:
            raise HTTPException(status_code=422, detail="用例不存在")

        # 获取测试环境
        env = await TestEnv.get_or_none(id=item.env_id)
        if not env:
            raise HTTPException(status_code=422, detail="测试环境不存在")

        # 获取使用的浏览器类型
        browser_type = item.browser_type if item.browser_type in ['chromium', 'firefox', 'webkit'] else 'chromium'

        # 创建一条执行记录
        case_record = await CaseRunRecords.create(case=case_)

        # 组装执行数据
        env_config = {
            "is_debug": False,
            "browser_type": browser_type,
            "host": env.host,
            "global_variable": env.global_vars
        }

        run_suite = {
            'id': 'demo',
            'name': '单用例执行',
            'setup_step': [],
            'cases': [
                {
                    "record_id": case_record.id,
                    'id': case_.id,
                    'name': case_.name,
                    'skip': False,
                    'steps': case_.steps
                }
            ]

        }

        # 调用引擎执行用例
        # runner = Runner(env_config, run_suite)
        # res = runner.run()

        # =====================将执行任务提交到任务队列中(RabbitMQ)=================
        mq.send_test_task(env_config, run_suite)
    return {"msg": "用例执行任务已提交，等待执行", "case_record": case_record.id}


# 执行套件
@router.post('/suites/{id}', tags=['测试运行'], summary='执行套件')
async def run_suites(id: int, item: RunForm):
    async with in_transaction():
        suite = await Suite.get_or_none(id=id).prefetch_related('cases')
        if not suite:
            raise HTTPException(status_code=422, detail="套件不存在")

        env = await TestEnv.get_or_none(id=item.env_id)
        if not env:
            raise HTTPException(status_code=422, detail="测试环境不存在")
        browser_type = item.browser_type if item.browser_type in ['chromium', 'firefox', 'webkit'] else 'chromium'

        env_config = {
            "is_debug": False,
            "browser_type": browser_type,
            "host": env.host,
            "global_variable": env.global_vars
        }

        suite_record = await SuiteRunRecords.create(suite=suite, env=env_config)

        cases = []
        for i in await suite.cases.all().order_by("sort"):
            case_ = await i.cases
            case_record = await CaseRunRecords.create(case=case_, suite_record=suite_record)
            cases.append({
                "record_id": case_record.id,
                'id': case_.id,
                'name': case_.name,
                'skip': i.skip,
                'steps': case_.steps
            })
        suite_record.all = len(cases)
        await suite_record.save()

        run_suite = {
            "suite_record_id": suite_record.id,
            'id': suite.id,
            'name': suite.name,
            'setup_step': suite.suite_setup_step,
            'cases': cases
        }
        mq.send_test_task(env_config, run_suite)
    return {"msg": "套件执行任务已提交，等待执行", "suite_record_id": suite_record.id}


# 执行测试任务
@router.post('/tasks/{id}', tags=['测试运行'], summary='执行测试任务')
async def run_tasks(id: int, item: RunForm):
    async with in_transaction():
        task = await Tasks.get_or_none(id=id).prefetch_related('suite', 'project')
        if not task:
            raise HTTPException(status_code=422, detail="任务不存在")
        env = await TestEnv.get_or_none(id=item.env_id)
        if not env:
            raise HTTPException(status_code=422, detail="测试环境不存在")
        browser_type = item.browser_type if item.browser_type in ['chromium', 'firefox', 'webkit'] else 'chromium'

        env_config = {
            "is_debug": False,
            "browser_type": browser_type,
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
    return {"msg": "任务已提交，等待执行", "task_record_id": task_record.id}


# 获取测试任务运行记录
@router.get('/tasks/records', tags=['测试报告'], summary='获取测试任务所有运行记录')
async def get_task_records(project_id: int, task_id: int = None, page: int = 1, page_size: int = 10):
    query = TaskRunRecords.filter(project=project_id)
    if task_id:
        query = query.filter(task=task_id)

    query = query.order_by('-id')
    total = await query.count()
    data = await query.offset((page - 1) * page_size).limit(page_size).prefetch_related('task')
    return {"total": total, "data": data}


#  获取测试套件运行记录
@router.get('/suites/records', tags=['测试报告'], summary='获取测试套件所有运行记录')
async def get_suite_records(suite_id: int = None, task_records_id: int = None, page: int = 1, page_size: int = 10):
    # suite 和 task 只能传一个
    query = SuiteRunRecords.all()
    if suite_id:
        query = query.filter(suite=suite_id)
    elif task_records_id:
        query = query.filter(task_run_records=task_records_id)
    else:
        raise HTTPException(status_code=422, detail="参数错误")
    query = query.order_by('-id')
    total = await query.count()
    data = await query.offset((page - 1) * page_size).limit(page_size).prefetch_related('suite')
    return {"total": total, "data": data}


#  获取用例运行记录
@router.get('/cases/records', tags=['测试报告'], summary='获取用例所有运行记录')
async def get_case_records(case_id: int = None, suite_records_id: int = None, page: int = 1, page_size: int = 10):
    # case 和 suite 只能传一个
    query = CaseRunRecords.all()
    if case_id:
        query = query.filter(case=case_id)
    elif suite_records_id:
        query = query.filter(suite_run_records=suite_records_id)
    else:
        raise HTTPException(status_code=422, detail="参数错误，至少传一个")
    query = query.order_by('-id')
    total = await query.count()
    data = await query.offset((page - 1) * page_size).limit(page_size).prefetch_related('case')
    return {"total": total, "data": data}


# 获取单条用例执行详情
@router.get('/cases/record/{id}', tags=['测试报告'], summary='获取单条用例运行详情')
async def get_case_record_detail(id: int):
    case_record = await CaseRunRecords.get_or_none(id=id)
    if not case_record:
        raise HTTPException(status_code=422, detail="用例执行记录不存在")
    return case_record


# 获取单个套件执行详情
@router.get('/suites/record/{id}', tags=['测试报告'], summary='获取单个套件运行详情', response_model=SuiteInfoSchemas)
async def get_suite_record_detail(id: int):
    suite_record = await SuiteRunRecords.get_or_none(id=id).prefetch_related('suite')
    if not suite_record:
        raise HTTPException(status_code=422, detail="套件执行记录不存在")
    res = SuiteInfoSchemas(**suite_record.__dict__, suite_name=suite_record.suite.name)
    return res


# 获取单个任务执行详情
@router.get('/tasks/record/{id}', tags=['测试报告'], summary='获取单个任务运行详情', response_model=TaskResultsSchemas)
async def get_task_record_detail(id: int):
    task_record = await TaskRunRecords.get_or_none(id=id).prefetch_related('task')
    if not task_record:
        raise HTTPException(status_code=422, detail="任务执行记录不存在")
    res = TaskResultsSchemas(**task_record.__dict__, task_name=task_record.task.name)
    return res
