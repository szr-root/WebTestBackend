# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2025/03/27
# @File : api.py
import json
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends, WebSocket
from apps.device.models import Device
from common.auth import is_authenticated
from .schemas import AddDeviceSchema
from redis.asyncio import Redis
from common.settings import REDIS_CONFIG

router = APIRouter(prefix='/api/node', tags=['设备管理'])


# 注册(创建)设备
@router.post('/devices', summary='注册设备', status_code=201)
# async def register_device(item: AddDeviceSchema, user_info: Dict = Depends(is_authenticated)):
async def register_device(item: AddDeviceSchema):
    # if not user_info['is_superuser']:
    #     raise HTTPException(status_code=403, detail='权限不足')
    # if await Device.get_or_none(id=item.id):
    #     raise HTTPException(status_code=400, detail='设备已存在')
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


# 订阅的websocket接口
@router.websocket('/ws/{device_id}')
async def websocket_subscribe(websocket: WebSocket, device_id: str):
    """websocket接口，订阅设备画面和日志"""
    # 链接redis
    redis_cli = Redis(host=REDIS_CONFIG.get('host'), port=REDIS_CONFIG.get('port'),
                      db=REDIS_CONFIG.get('db_subscribe'), password=REDIS_CONFIG.get('password'))

    await websocket.accept()
    # 初始化订阅器
    pubsub = redis_cli.pubsub()
    try:
        # 订阅频道
        await pubsub.subscribe(f'{device_id}:screen', f'{device_id}:log')
        # 循环接受订阅消息
        async for message in pubsub.listen():
            try:
                if message['type'] == 'message':
                    # 判断频道
                    if message['channel'].decode() == f'{device_id}:screen':
                        # 获取消息内容
                        data = json.dumps({
                            "type": "screen",
                            "data": message['data'].decode()
                        })
                        # 接收到消息，发送给客户端
                        await websocket.send_text(data)
                    elif message['channel'].decode() == f'{device_id}:log':
                        # 获取消息内容
                        data = json.dumps({
                            "type": "log",
                            "data": message['data'].decode()
                        })
                        await websocket.send_text(data)

            except Exception as e:
                print(f'订阅数据处理发生错误: {e}')
    except Exception as e:
        await redis_cli.close()
        print('websocket连接错误')
        # 取消订阅事件
        await pubsub.unsubscribe(f'{device_id}:screen')


# 根据time_id 获取设备信息
@router.get('/devices/{time_id}', summary='根据time_id 获取设备信息')
async def get_device_info(time_id: str, user_info: Dict = Depends(is_authenticated)):
    # 根据redis获取设备信息
    redis_cli = Redis(host=REDIS_CONFIG.get('host'), port=REDIS_CONFIG.get('port'),
                      db=REDIS_CONFIG.get('db_subscribe'), password=REDIS_CONFIG.get('password'))
    device_id = await redis_cli.get(time_id)
    if not device_id:
        raise HTTPException(status_code=422, detail='当前任务未运行，未分配执行设备')
    else:
        device_id = int(device_id.decode())
        device = await Device.get_or_none(id=device_id)
        return device
