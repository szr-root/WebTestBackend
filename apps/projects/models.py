# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : models.py

from tortoise import fields, models


class TestProject(models.Model):
    id = fields.IntField(pk=True, description="项目id")
    name = fields.CharField(max_length=32, description="项目名称")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    user = fields.ForeignKeyField('models.Users', related_name='projects', description="项目负责人")

    def __str__(self):
        return self.name

    class Meta:
        table = "test_project"
        table_description = "测试表"


class TestEnv(models.Model):
    id = fields.IntField(pk=True, description="环境id")
    name = fields.CharField(max_length=32, description="环境名称")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    project = fields.ForeignKeyField('models.TestProject', related_name='envs', description="所属项目")
    host = fields.CharField(max_length=255, description="环境地址")
    global_vars = fields.JSONField(description="全局变量", default=dict)

    def __str__(self):
        return self.name

    class Meta:
        table = "test_env"
        table_description = "测试环境表"


class ProjectModule(models.Model):
    """
    项目模块表
    """
    id = fields.IntField(pk=True, description="模块id")
    name = fields.CharField(max_length=32, description="模块名称")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    project = fields.ForeignKeyField('models.TestProject', related_name='modules', description="所属项目")

    def __str__(self):
        return self.name

    class Meta:
        table = "project_module"
        table_description = "项目模块表"
