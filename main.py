import uvicorn
from fastapi import FastAPI
from common import settings
from tortoise.contrib.fastapi import register_tortoise
from apps.users.api import router as user_router
from apps.projects.api import router as project_router
from apps.testmanage.api import router as test_router
from apps.testplan.api import router as plan_router

app = FastAPI(
    title="Web测试平台接口文档",
    description="FastApi",
    version="0.0.1"
)

register_tortoise(app, config=settings.TORTOISE_ORM, modules={'models': ['models']})

# 注册路由
app.include_router(user_router)
app.include_router(project_router)
app.include_router(test_router)
app.include_router(plan_router)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
