# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/12
# @File : schemas.py
from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel, Field


class RunForm(BaseModel):
    env_id: int = Field(..., title='运行环境id')
    browser_type: str | None = Field(default=None, description='浏览器类型')
    # 分布式才用到
    dev_id: str | None = Field(default=None, description='设备id')


class SuiteInfoSchemas(BaseModel):
    id: int
    status: str
    suite_id: int
    task_run_records_id: int
    suite_name: str
    success: int
    error: int
    skip: int
    duration: float
    pass_rate: int
    run_all: int
    all: int
    fail: int
    suite_log: List
    no_run: int
    env: Dict


class TaskResultsSchemas(BaseModel):
    project_id: int
    start_time: datetime
    task_id: int
    task_name: str
    success: int
    error: int
    skip: int
    all: int
    fail: int
    run_all: int
    status: str
    id: int
    env: Dict
