# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2025/03/27
# @File : models.py
from tortoise import models, fields


class Device(models.Model):
    """执行设备"""
    id = fields.CharField(primary_key=True, max_length=150, description="设备id")
    ip = fields.CharField(max_length=50, description="设备ip")
    name = fields.CharField(max_length=50, description="设备名称")
    system = fields.CharField(max_length=50, description="设备系统")
    status = fields.CharField(max_length=50, description="设备状态",
                              choices=['在线', '离线', '执行任务中'],
                              default="在线")
