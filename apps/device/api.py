# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2025/03/27
# @File : api.py
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends
from apps.device.models import Device
from common.auth import is_authenticated
from .schemas import AddDeviceSchema

router = APIRouter(prefix='/api/node', tags=['设备管理'])


# 注册(创建)设备
@router.post('/devices', summary='注册设备', status_code=201)
async def register_device(item: AddDeviceSchema, user_info: Dict = Depends(is_authenticated)):
    if not user_info['is_superuser']:
        raise HTTPException(status_code=403, detail='权限不足')
    if await Device.get_or_none(id=item.id):
        raise HTTPException(status_code=400, detail='设备已存在')
    try:
        device = await Device.create(**item.dict())
        return device
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 获取设备列表
@router.get('/devices', summary='获取设备列表')
async def get_devices(page: int = 1, size: int = 10, user_info: Dict = Depends(is_authenticated)):
    query = Device.all()
    # 分页
    total = await query.count()
    devices = await query.offset((page - 1) * size).limit(size).all()
    result = []
    for dev in devices:
        result.append({
            'id': dev.id,
            'ip': dev.ip,
            'name': dev.name,
            'status': dev.status,
            'system': dev.system
        })
    return {"total": total, 'data': result}


# 删除设备
@router.delete('/devices/{id}', summary='删除设备', status_code=204)
async def delete_device(id: int, user_info: Dict = Depends(is_authenticated)):
    if not user_info['is_superuser']:
        raise HTTPException(status_code=403, detail='无权删除设备')
    device = await Device.get_or_none(id=id)
    if not device:
        raise HTTPException(status_code=404, detail='设备不存在')
    await device.delete()
    return {'message': '设备已删除'}
