# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : schemas.py
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TaskSchema(BaseModel):
    id: int = Field(description="任务id")
    name: str = Field(description="任务名称")
    project_id: int = Field(description="所属项目")
    create_time: datetime = Field(description="创建时间")


class AddTaskForm(BaseModel):
    name: str = Field(description="任务名称", max_length=20)
    project_id: int = Field(description="所属项目")


class UpdateTaskNameForm(BaseModel):
    name: str = Field(description="任务名称", max_length=20)


class AddSuiteToTaskForm(BaseModel):
    suite_id: int = Field(description="业务流id")


class TaskToSuiteSchema(BaseModel):
    suite_id: int = Field(description="业务流id")
    suite_name: str = Field(description="业务流名称")
    suite_type: str = Field(description="业务流类型")


class TaskDetailSchema(BaseModel):
    id: int = Field(description="任务id")
    name: str = Field(description="任务名称")
    create_time: datetime = Field(description="创建时间")
    suites: List[TaskToSuiteSchema] = Field(description="任务中的业务流")
