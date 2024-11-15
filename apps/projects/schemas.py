# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : schemas.py
from typing import List, Dict

from pydantic import BaseModel, Field
from datetime import datetime


class AddProjectForm(BaseModel):
    name: str = Field(description="项目名称", max_length=20)
    user: int = Field(description="项目负责人")


class ProjectSchemas(BaseModel):
    id: int = Field(description="项目id")
    name: str = Field(description="项目名称", max_length=20)
    user_id: int = Field(description="项目负责人")
    create_time: datetime = Field(description="创建时间")


class UpdateProjectForm(BaseModel):
    name: str = Field(description="项目名称", max_length=20)


class ProListSchemas(ProjectSchemas):
    user_name: str = Field(description="项目负责人")


class ProjectPageListSchemas(BaseModel):
    total: int = Field(description="总数")
    data: List[ProListSchemas] = Field(description="数据")


# =====================================测试环境相关的接口=================================
class TestEnvSchemas(BaseModel):
    id: int = Field(description="环境id")
    name: str = Field(description="环境名称")
    create_time: datetime = Field(description="创建时间")
    host: str = Field(description="环境地址")
    global_vars: dict = Field(description="全局变量")
    project_id: int = Field(description="所属项目")


class AddEnvForm(BaseModel):
    """创建测试环境"""
    project_id: int = Field(description="所属项目")
    name: str = Field(description="环境名称")
    host: str = Field(description="环境地址")
    global_vars: Dict = Field(description="全局变量", default=dict)


class UpdateEnvForm(BaseModel):
    """修改测试环境"""
    name: str | None = Field(default=None, description="环境名称")
    host: str | None = Field(default=None, description="环境地址")
    global_vars: Dict | None = Field(default=None, description="全局变量")


# =====================================项目测试模块相关的数据模型=================================
class ProjectModuleSchemas(BaseModel):
    id: int = Field(description="模块id")
    name: str = Field(description="模块名称")
    project_id: int = Field(description="所属项目")
    create_time: datetime = Field(description="创建时间")


class AddModuleForm(BaseModel):
    """创建测试模块"""
    project_id: int = Field(description="所属项目")
    name: str = Field(description="模块名称")


class UpdateModuleForm(BaseModel):
    """修改测试模块"""
    name: str = Field(description="模块名称")