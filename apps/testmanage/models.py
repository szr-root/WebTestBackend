# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/12
# @File : models.py

from tortoise import models, fields


class Suite(models.Model):
    """ 测试套件 """
    id = fields.IntField(pk=True, description="套件id")
    name = fields.CharField(max_length=32, description="套件名称")
    project = fields.ForeignKeyField('models.TestProject', related_name='suites', description="所属项目")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    modules = fields.ForeignKeyField('models.ProjectModule', related_name='suites', description="所属模块", null=True,
                                     blank=True)
    suite_setup_step = fields.JSONField(description="前置执行步骤", default=list)
    suite_type = fields.CharField(max_length=50, description="套件类型",
                                  choices=[(1, "功能"), (2, "业务流")],
                                  default="业务流"
                                  )

    def __str__(self):
        return self.name

    class Meta:
        table = "suite"
        table_description = "测试套件"


class Cases(models.Model):
    id = fields.IntField(pk=True, description=" 用例id")
    name = fields.CharField(max_length=32, description="用例名称")
    project = fields.ForeignKeyField('models.TestProject', related_name='cases', description="所属项目")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    steps = fields.JSONField(description="用例执行步骤", default=list)

    def __str__(self):
        return self.name

    class Meta:
        table = "cases"
        table_description = "测试用例"


class SuiteToCase(models.Model):
    """中间表"""
    id = fields.IntField(pk=True, description="关联id")
    suite = fields.ForeignKeyField('models.Suite', related_name='cases', description="所属套件")
    cases = fields.ForeignKeyField('models.Cases', related_name='suites', description="所属用例")
    sort = fields.IntField(description="用例执行排序")
    skip = fields.BooleanField(default=False, description="用例在某个套件是否跳过")
