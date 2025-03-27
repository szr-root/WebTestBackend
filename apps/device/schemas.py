# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2025/03/27
# @File : schemas.py

from pydantic import BaseModel, Field


class AddDeviceSchema(BaseModel):
    id: str = Field(description="设备id")
    ip: str = Field(description="设备ip")
    name: str = Field(description="设备名称")
    system: str = Field(description="设备系统")
    status: str = Field(description="设备状态", default='在线')
