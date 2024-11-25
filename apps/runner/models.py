# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/12
# @File : models.py

from tortoise import models, fields


class TaskRunRecords(models.Model):
    """测试任务运行记录表"""
    id = fields.IntField(pk=True, description="套件记录id")
    project = fields.ForeignKeyField("models.TestProject", related_name="task_records", description="所属项目")
    task = fields.ForeignKeyField("models.Tasks", related_name="task_records", description="执行的任务")
    env = fields.JSONField(description="执行环境", default=dict)
    start_time = fields.DatetimeField(auto_now_add=True, description="开始执行时间")
    status = fields.CharField(max_length=255, description="运行状态",
                              choices=[("执行完成", "执行完成"), ("执行中", "执行中")],
                              default="执行中")

    all = fields.IntField(description="总用例数", default=0)
    run_all = fields.IntField(description="执行用例数", default=0)
    no_run = fields.IntField(description="未执行用例数", default=0)
    success = fields.IntField(description="成功用例数", default=0)
    fail = fields.IntField(description="失败用例数", default=0)
    error = fields.IntField(description="错误用例数", default=0)
    skip = fields.IntField(description="跳过用例数", default=0)

    class Meta:
        table = "task_run_records"
        table_description = "测试任务运行记录表"


class SuiteRunRecords(models.Model):
    """测试套件运行记录表"""
    id = fields.IntField(pk=True, description="记录id")
    suite = fields.ForeignKeyField("models.Suite", related_name="suite_records", description="执行的套件")
    task_run_records = fields.ForeignKeyField("models.TaskRunRecords", related_name="suite_records",
                                              description="关联的运行任务记录", null=True, blank=True)
    status = fields.CharField(max_length=255, description="运行状态",
                              choices=[("等待执行", "等待执行"), ("执行中", "执行中"), ("执行完成", "执行完成")],
                              default="等待执行")
    all = fields.IntField(description="总用例数", default=0)
    run_all = fields.IntField(description="执行用例数", default=0)
    no_run = fields.IntField(description="未执行用例数", default=0)
    success = fields.IntField(description="成功用例数", default=0)
    fail = fields.IntField(description="失败用例数", default=0)
    error = fields.IntField(description="错误用例数", default=0)
    skip = fields.IntField(description="跳过用例数", default=0)
    duration = fields.FloatField(description="执行时间", default=0)
    suite_log = fields.JSONField(description="套件执行日志", default=list)
    pass_rate = fields.FloatField(description="通过率", default=0)
    env = fields.JSONField(description="执行环境", default=dict, null=True, blank=True)

    class Meta:
        table = "suite_run_records"
        table_description = "测试套件运行记录表"


class CaseRunRecords(models.Model):
    """测试用例运行记录表"""
    id = fields.IntField(pk=True, description="用例记录id")
    case = fields.ForeignKeyField("models.Cases", related_name="case_records", description="执行的用例")
    suite_run_records = fields.ForeignKeyField("models.SuiteRunRecords", related_name="case_records",
                                               description="关联的运行套件记录", null=True, blank=True)
    state = fields.CharField(max_length=255, description="运行状态",
                             choices=[("success", "成功"), ("fail", "失败"), ("error", "错误"), ("skip", "跳过"),
                                      ("no_run", "未执行"), ("running", "执行中")],
                             default="running")
    run_info = fields.JSONField(description="用例执行详情", default=dict)

    class Meta:
        table = "case_run_records"
        table_description = "测试用例运行记录表"
