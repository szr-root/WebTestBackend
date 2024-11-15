# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : models.py

from tortoise import models, fields


class Tasks(models.Model):
    id = fields.IntField(pk=True, description="任务id")
    name = fields.CharField(max_length=32, description="任务名称")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    project = fields.ForeignKeyField('models.TestProject', related_name='tasks', description="所属项目")
    suite = fields.ManyToManyField('models.Suite', related_name='tasks', description="任务中的套件", null=True, blank=True,
                                   default=[])

    class Meta:
        table = 'tasks'
        table_description = '测试任务表'
