# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : api.py
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends
from .schemas import AddProjectForm, ProjectSchemas, UpdateProjectForm, AddEnvForm, TestEnvSchemas, UpdateEnvForm, \
    ProjectModuleSchemas, AddModuleForm, UpdateModuleForm
from .models import TestProject, TestEnv, ProjectModule
from apps.users.models import Users
from common.auth import is_authenticated

router = APIRouter(prefix='/api/pro')


# 创建项目
@router.post('/projects', tags=["项目管理"], summary="创建项目", status_code=201, response_model=ProjectSchemas)
async def create_project(item: AddProjectForm, user_info: Dict = Depends(is_authenticated)):
    user = await Users.get_or_none(id=item.user)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    if (user.id != user_info['id']) and user_info['is_superuser'] is not True:
        raise HTTPException(status_code=400, detail="token信息与登录用户不一致")
    pro = await TestProject.create(name=item.name, user=user)
    return pro


# 修改项目
@router.put("/projects/{id}/", tags=["项目管理"], summary="修改项目", status_code=200, response_model=ProjectSchemas)
async def update_project(id: int, item: UpdateProjectForm, user_info: dict = Depends(is_authenticated)):
    pro = await TestProject.get_or_none(id=id).prefetch_related("user")
    if not pro:
        raise HTTPException(status_code=422, detail="项目不存在")
    if (pro.user.id != user_info['id']) and user_info['is_superuser'] is not True:
        raise HTTPException(status_code=400, detail="用户只能修改自己创建的项目")
    pro.name = item.name
    await pro.save()
    return pro


# 删除项目
@router.delete("/projects/{id}/", tags=["项目管理"], summary="删除项目", status_code=204)
async def delete_project(id: int, user_info: Dict = Depends(is_authenticated)):
    pro = await TestProject.get_or_none(id=id).prefetch_related("user")
    if not pro:
        raise HTTPException(status_code=422, detail="项目不存在")
    if (pro.user.id != user_info['id']) and user_info['is_superuser'] is not True:
        raise HTTPException(status_code=400, detail="用户只能删除自己创建的项目")
    await pro.delete()


# 获取项目列表
@router.get("/projects/", tags=["项目管理"], summary="获取项目列表", status_code=200, response_model=List[ProjectSchemas])
async def get_projects(user_info: Dict = Depends(is_authenticated)):
    # 超级管理员查看所有，普通用户只能查看自己的项目
    if user_info['is_superuser'] is True:
        pros = await TestProject.all().prefetch_related("user")
    else:
        pros = await TestProject.filter(user=user_info['id']).prefetch_related("user")
    return pros


# 获取项目详情
@router.get("/projects/{id}/", tags=["项目管理"], summary="获取单个项目详情", status_code=200, response_model=ProjectSchemas)
async def get_project(id: int, user_info: Dict = Depends(is_authenticated)):
    pro = await TestProject.get_or_none(id=id).prefetch_related("user")
    if not pro:
        raise HTTPException(status_code=422, detail="项目不存在")
    return pro


# ===================================测试环境的增删查改接口==============================================

# 创建测试环境
@router.post('/envs', tags=['测试环境管理'], summary='创建测试环境', status_code=201, response_model=TestEnvSchemas)
async def create_env(item: AddEnvForm, user_info: Dict = Depends(is_authenticated)):
    # 方式一
    # env = await TestEnv.create(**item.dict())
    # 方式二
    # env = await TestEnv.create(name=item.name, host=item.host, global_vars=item.global_vars, project_id=item.project_id)
    # 方式三
    project = await TestProject.get_or_none(id=item.project_id)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    env = await TestEnv.create(name=item.name, host=item.host, global_vars=item.global_vars, project=project)
    return env


# 获取测试环境列表
@router.get('/envs', tags=['测试环境管理'], summary='获取测试环境列表', response_model=list[TestEnvSchemas])
async def get_envs(project: int | None = None, user_info: Dict = Depends(is_authenticated)):
    query = TestEnv.all()
    if project:
        project = await TestProject.get_or_none(id=project)
        query = query.filter(project=project)
    envs = await query
    return envs


# 获取单个测试环境详情
@router.get('/envs/{id}', tags=['测试环境管理'], summary='获取单个测试环境详情', response_model=TestEnvSchemas)
async def get_env(id: int, user_info: Dict = Depends(is_authenticated)):
    env = await TestEnv.get_or_none(id=id)
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    return env


# 删除测试环境
@router.delete('/envs/{id}', tags=['测试环境管理'], summary='删除测试环境', status_code=204)
async def delete_env(id: int, user_info: Dict = Depends(is_authenticated)):
    env = await TestEnv.get_or_none(id=id)
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    await env.delete()


# 修改测试环境
@router.put('/envs/{id}', tags=['测试环境管理'], summary='修改测试环境', response_model=TestEnvSchemas)
async def update_env(id: int, item: UpdateEnvForm, user_info: Dict = Depends(is_authenticated)):
    env = await TestEnv.get_or_none(id=id)
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    env = await env.update_from_dict(item.dict(exclude_unset=True))
    await env.save()
    return env


# ===================================测试模块的增删查改接口==============================================
# 创建测试模块
@router.post('/modules', tags=['测试模块管理'], summary='创建测试模块', status_code=201,
             response_model=ProjectModuleSchemas)
async def create_module(item: AddModuleForm, user_info: dict = Depends(is_authenticated), ):
    project = await TestProject.get_or_none(id=item.project_id)
    if not project:
        raise HTTPException(status_code=422, detail="传入的项目ID不存在")
    module = await ProjectModule.create(name=item.name, project=project)
    return module


# 获取测试模块列表
@router.get('/modules', tags=['测试模块管理'], summary='获取测试模块列表')
async def get_modules(project: int | None = None, user_info: dict = Depends(is_authenticated)):
    query = ProjectModule.all()
    if project:
        project = await TestProject.get_or_none(id=project)
        query = query.filter(project=project)

    modules = await query
    return modules


# 获取单个测试模块详情
@router.get('/modules/{id}', tags=['测试模块管理'], summary='获取单个测试模块详情')
async def get_module(id: int, user_info: dict = Depends(is_authenticated)):
    module = await ProjectModule.get_or_none(id=id)
    if not module:
        raise HTTPException(status_code=422, detail="模块不存在")
    return module


# 删除测试模块
@router.delete('/modules/{id}', tags=['测试模块管理'], summary='删除测试模块', status_code=204)
async def delete_module(id: int, user_info: dict = Depends(is_authenticated)):
    module = await ProjectModule.get_or_none(id=id)
    if not module:
        raise HTTPException(status_code=422, detail="模块不存在")
    await module.delete()


# 修改测试模块
@router.put('/modules/{id}', tags=['测试模块管理'], summary='修改测试模块', response_model=ProjectModuleSchemas)
async def update_module(id: int, item: UpdateModuleForm, user_info: dict = Depends(is_authenticated)):
    module = await ProjectModule.get_or_none(id=id)
    if not module:
        raise HTTPException(status_code=422, detail="模块不存在")
    module.name = item.name
    await module.save()
    return module
