# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : api.py
from typing import Annotated, List

from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, HTTPException, Depends
from apps.projects.models import TestProject
from apps.testplan.schemas import AddTaskForm, TaskSchema, UpdateTaskNameForm, AddSuiteToTaskForm
from .models import Tasks
from common import auth
from ..testmanage.models import Suite

router = APIRouter(prefix="/api/plan")


# 创建测试任务
@router.post("/tasks", tags=['测试任务'], summary="创建测试任务", status_code=201, response_model=TaskSchema)
async def create_task(item: AddTaskForm):
    project = await TestProject.get_or_none(id=item.project_id)
    if not project:
        raise HTTPException(status_code=422, detail='项目不存在')
    task = await Tasks.create(**item.dict(exclude_unset=True))
    return task


# 获取测试任务列表
@router.get("/tasks", tags=['测试任务'], summary="获取测试任务列表", response_model=List[TaskSchema])
async def get_tasks(project_id: int):
    return await Tasks.filter(project_id=project_id).all()


# 删除测试任务
@router.delete("/tasks/{id}", tags=['测试任务'], summary="删除测试任务", status_code=204)
async def delete_task(id: int):
    task = await Tasks.get_or_none(id=id)
    if not task:
        raise HTTPException(status_code=422, detail='任务不存在')
    await task.delete()


# 修改任务名称
@router.put("/tasks/{id}", tags=['测试任务'], summary="修改测试任务名称", response_model=TaskSchema)
async def update_task(id: int, item: UpdateTaskNameForm):
    task = await Tasks.get_or_none(id=id)
    if not task:
        raise HTTPException(status_code=422, detail='任务不存在')
    task.name = item.name
    await task.save()
    return task


# 往任务中增加业务流（套件）
@router.post("/tasks/{id}/suite/", tags=['测试任务'], summary="往任务中增加业务流", status_code=201)
async def add_suite_to_task(id: int, item: AddSuiteToTaskForm):
    task = await Tasks.get_or_none(id=id)
    if not task:
        raise HTTPException(status_code=422, detail='任务不存在')
    suite = await Suite.get_or_none(id=item.suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail='业务流不存在')
    await task.suite.add(suite)
    return task


# 从任务中删除业务流
@router.delete("/tasks/{id}/suite/{suite_id}", tags=['测试任务'], summary="从任务中删除业务流", status_code=204)
async def delete_suite_from_task(id: int, suite_id: int):
    task = await Tasks.get_or_none(id=id)
    if not task:
        raise HTTPException(status_code=422, detail='任务不存在')
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail='业务流不存在')
    await task.suite.remove(suite)
