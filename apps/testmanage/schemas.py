# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/12
# @File : schemas.py
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SuiteSchemas(BaseModel):
    """ 测试套件返回数据类型 """
    id: int = Field(description="套件id")
    name: str = Field(max_length=32, description="套件名称")
    project_id: int = Field(description="所属项目id")
    create_time: datetime = Field(description="创建时间")
    modules_id: int = Field(description="所属模块id")
    suite_setup_step: list = Field(description="前置执行步骤")
    suite_type: str = Field(description="套件类型", choices=["功能", "业务流"], )


class AddSuiteForm(BaseModel):
    """创建套件参数"""
    name: str = Field(max_length=32, description="套件名称")
    project_id: int = Field(description="所属项目id")
    modules_id: int = Field(description="所属模块id")
    suite_setup_step: list = Field(description="前置执行步骤")
    suite_type: str = Field(description="套件类型")


class UpdateSuiteForm(BaseModel):
    """ 修改"""
    name: str | None = Field(max_length=32, description="套件名称", default=None)
    modules_id: int | None = Field(description="所属模块id", default=None)
    suite_setup_step: list = Field(description="前置执行步骤", default=list)
    suite_type: str | None = Field(description="套件类型", default=None)


# ============================================测试用例的数据模型============================================


class CasesSchemas(BaseModel):
    id: int = Field(description=" 用例id")
    name: str = Field(description="用例名称")
    project_id: int = Field(description="所属项目")
    create_time: datetime = Field(description="创建时间")
    steps: List = Field(description="用例执行步骤")


class AddCasesForm(BaseModel):
    name: str = Field(description="用例名称")
    project_id: int = Field(description="所属项目")
    steps: List = Field(description="用例执行步骤")


class UpdateCasesForm(BaseModel):
    name: str | None = Field(description="用例名称", default=None)
    steps: List | None = Field(description="用例执行步骤", default=None)


class CasesListSchema(BaseModel):
    id: int = Field(description=" 用例id")
    name: str = Field(description="用例名称")
    project_id: int = Field(description="所属项目")
    create_time: datetime = Field(description="创建时间")


# ============================================套件中用例管理的数据模型============================================


class SuiteToCaseSchema(BaseModel):
    id: int = Field(description="关联id")
    suite_id: int = Field(description="所属套件")
    cases_id: int = Field(description="所属用例")
    sort: int = Field(description="用例执行顺序")
    skip: bool = Field(description="用例在某个套件是否跳过")


class SuiteToCaseListSchema(SuiteToCaseSchema):
    """获取套件中所有用例"""
    suite_name: str = Field(description="套件名称")
    cases_name: str = Field(description="用例名称")


class AddSuiteToCaseForm(BaseModel):
    cases_id: int = Field(description="所属用例")
    sort: int = Field(description="用例执行顺序")


class UpdateSuiteToCaseForm(BaseModel):
    suite_id: int = Field(description="所属套件")
    cases_id: int = Field(description="所属用例")


class UpdateCasesSortForm(BaseModel):
    id: int = Field(description="用例id")
    sort: int = Field(description="用例执行顺序")
