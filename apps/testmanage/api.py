# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/12
# @File : api.py
from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Depends
from common import auth
from common.auth import is_authenticated
from .schemas import SuiteSchemas, AddSuiteForm, UpdateSuiteForm, AddCasesForm, UpdateCasesForm, CasesSchemas, \
    CasesListSchema, SuiteToCaseSchema, AddSuiteToCaseForm, SuiteToCaseListSchema, UpdateCasesSortForm
from apps.projects.models import TestProject, ProjectModule
from .models import Suite, Cases, SuiteToCase

# 创建路由对象
from ..runner.models import CaseRunRecords, SuiteRunRecords

router = APIRouter(prefix='/api/test', dependencies=[Depends(is_authenticated)])


# =====================测试套件的接口=====================

# 创建测试套件
@router.post('/suites/', tags=['测试套件管理'], summary='创建测试套件', status_code=201, response_model=SuiteSchemas)
async def create_suite(item: AddSuiteForm):
    project = await TestProject.get_or_none(id=item.project_id)
    if not project:
        raise HTTPException(status_code=404, detail='项目不存在')
    modules = await ProjectModule.get_or_none(id=item.modules_id)
    if not modules:
        raise HTTPException(status_code=404, detail='模块不存在')
    suite = await Suite.create(**item.dict(exclude_unset=True))
    return suite


# 查询测试套件列表
@router.get('/suites/', tags=['测试套件管理'], summary='查询测试套件列表', status_code=200)
async def get_suites(project_id: int | None = None, modules_id: int | None = None, page: int = 1, size: int = 10):
    query = Suite.all()
    project = await TestProject.get_or_none(id=project_id)
    if project:
        query = query.filter(project=project)
    modules = await ProjectModule.get_or_none(id=modules_id)
    if modules:
        query = query.filter(modules=modules)

    total = await query.count()
    suites = await query.offset((page - 1) * size).limit(size).prefetch_related('cases')
    result = []
    for suite in suites:
        modules = await suite.modules
        result.append({
            "id": suite.id,
            "create_time": suite.create_time,
            "name": suite.name,
            "suite_type": suite.suite_type,
            "suite_setup_step": len(suite.suite_setup_step),
            "modules": modules.name if modules else "",
            "case_count": len(suite.cases),
            "run_count": await SuiteRunRecords.filter(suite=suite.id).count(),
        })
    return {
        "total": total,
        "data": result,
        "page": page,
        "size": size,
    }
    # suites = await query.all()
    # return suites


# 查询单个套件详情
@router.get('/suites/{id}/', tags=['测试套件管理'], summary='查询单个套件详情', status_code=200, response_model=SuiteSchemas)
async def get_suite_detail(id: int):
    suite = await Suite.get_or_none(id=id)
    if not suite:
        raise HTTPException(status_code=404, detail='套件不存在')
    return suite


# 删除套件
@router.delete('/suites/{id}/', tags=['测试套件管理'], summary='删除套件', status_code=204)
async def delete_suite(id: int):
    suite = await Suite.get_or_none(id=id)
    if not suite:
        raise HTTPException(status_code=404, detail='套件不存在')
    await suite.delete()


# 更改套件信息
@router.put('/suites/{id}/', tags=['测试套件管理'], summary='更改套件信息', status_code=200, response_model=SuiteSchemas)
async def update_suite(id: int, item: UpdateSuiteForm):
    suite = await Suite.get_or_none(id=id)
    if not suite:
        raise HTTPException(status_code=404, detail='套件不存在')
    module = await ProjectModule.get_or_none(id=item.modules_id)
    if not module:
        raise HTTPException(status_code=422, detail='模块不存在')
    await suite.update_from_dict(item.dict(exclude_unset=True)).save()
    return suite


# =====================测试用例的接口=====================

# 创建测试用例
@router.post('/cases/', tags=['测试用例管理'], summary='创建测试用例', status_code=201, response_model=CasesSchemas)
async def create_cases(item: AddCasesForm):
    project = await TestProject.get_or_none(id=item.project_id)
    if not project:
        raise HTTPException(status_code=422, detail='项目不存在')
    cases = await Cases.create(**item.dict(exclude_unset=True))
    return cases


# 更改用例信息
@router.put('/cases/{id}/', tags=['测试用例管理'], summary='更改用例信息', status_code=200, response_model=CasesSchemas)
async def update_cases(id: int, item: UpdateCasesForm):
    cases = await Cases.get_or_none(id=id)
    if not cases:
        raise HTTPException(status_code=422, detail='用例不存在')
    await cases.update_from_dict(item.dict(exclude_unset=True)).save()
    return cases


# 查询单个用例详情
@router.get('/cases/{id}/', tags=['测试用例管理'], summary='查询单个用例详情', status_code=200, response_model=CasesSchemas)
async def get_cases_detail(id: int):
    cases = await Cases.get_or_none(id=id)
    if not cases:
        raise HTTPException(status_code=404, detail='用例不存在')
    return cases


# 删除用例
@router.delete('/cases/{id}/', tags=['测试用例管理'], summary='删除用例', status_code=204)
async def delete_cases(id: int):
    cases = await Cases.get_or_none(id=id)
    if not cases:
        raise HTTPException(status_code=404, detail='用例不存在')

    # 确保用例没有被其他套件引用才能删除
    query = SuiteToCase.filter(cases=cases)
    if await query.exists():
        raise HTTPException(status_code=422, detail='用例被套件引用，无法删除')
    await cases.delete()


# 复制用例
@router.post('/cases/{id}/', tags=['测试用例管理'], summary='复制用例', status_code=201, response_model=CasesSchemas)
async def copy_cases(id: int):
    cases = await Cases.get_or_none(id=id).prefetch_related('project')
    if not cases:
        raise HTTPException(status_code=404, detail='用例不存在')
    new_cases = await Cases.create(name=cases.name + "_copy", project=cases.project, steps=cases.steps)
    return new_cases


# 查询测试用例列表
@router.get('/cases/', tags=['测试用例管理'], summary='查询测试用例列表', status_code=200)
async def get_cases(project_id: int, page: int = 1, size: int = 10):
    query = Cases.filter(project=project_id)
    cases = await query.offset((page - 1) * size).limit(size)
    total = await query.count()
    result = []
    for i in cases:
        # 历史执行次数
        run_count = await CaseRunRecords.filter(case=i).count()
        # 最近一次状态
        run_record = await CaseRunRecords.filter(case=i).order_by('-id').first()
        state = run_record.state if run_record else "未执行"
        # 用例步骤
        result.append({
            "id": i.id,
            "name": i.name,
            "steps": len(i.steps),
            "create_time": i.create_time,
            "state": state,
            "run_count": run_count,
        })
    return {"page": page, "size": size, "total": total, "data": result}


# =====================测试套件中用例管理的接口=====================
# 添加用例到套件中
@router.post('/suites/{suite_id}/cases/', tags=['套件管理'], summary='添加用例到套件中', status_code=201,
             response_model=SuiteToCaseSchema)
async def add_cases_to_suite(suite_id: int, item: AddSuiteToCaseForm):
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail='套件不存在')
    case_ = await Cases.get_or_none(id=item.cases_id)
    if not case_:
        raise HTTPException(status_code=404, detail='用例不存在')
    return await SuiteToCase.create(suite=suite, cases=case_, sort=item.sort)


# 删除套件中的用例
@router.delete('/suites/{suite_id}/cases/{id}/', tags=['套件管理'], summary='删除套件中的用例', status_code=204)
async def delete_cases_from_suite(id: int, suite_id: int):
    suite_to_case = await SuiteToCase.get_or_none(id=id, suite_id=suite_id)
    if not suite_to_case:
        raise HTTPException(status_code=404, detail='套件中不存在该用例')
    await suite_to_case.delete()


# 获取套件中所有用例
@router.get('/suites/{suite_id}/cases/', tags=['套件管理'], summary='获取套件中所有用例', status_code=200,
            response_model=List[SuiteToCaseListSchema])
async def get_cases_from_suite(suite_id: int):
    suite_to_case = await SuiteToCase.filter(suite_id=suite_id).prefetch_related("cases", "suite").order_by("sort")
    result = [{
        "id": case.id,
        "skip": case.skip,
        "sort": case.sort,
        "suite_id": case.suite_id,
        "cases_id": case.cases.id,
        "cases_name": case.cases.name,
        "suite_name": case.suite.name,
    } for case in suite_to_case]
    return result


# 修改套件中用例执行状态（是否跳过执行）
@router.put('/suites/{suite_id}/cases/{id}/', tags=['套件管理'], summary='修改是否跳过执行状态', status_code=200,
            response_model=SuiteToCaseSchema)
async def update_cases_sort(id: int, suite_id: int):
    suite_to_case = await SuiteToCase.get_or_none(id=id, suite_id=suite_id)
    if not suite_to_case:
        raise HTTPException(status_code=404, detail='套件用例不存在')

    suite_to_case.skip = not suite_to_case.skip
    await suite_to_case.save()
    return suite_to_case


# 修改用例执行顺序
@router.post('/suites/{suite_id}/cases/sort/', tags=['套件管理'], summary='修改用例执行顺序', status_code=200)
async def update_cases_sort(suite_id: int, item: List[UpdateCasesSortForm]):
    for i in item:
        suite_to_case = await SuiteToCase.get_or_none(id=i.id, suite_id=suite_id)
        suite_to_case.sort = i.sort
        await suite_to_case.save()
    return await SuiteToCase.filter(suite_id=suite_id).order_by("sort")
