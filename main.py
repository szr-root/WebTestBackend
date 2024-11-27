import uvicorn
from fastapi import FastAPI
from common import settings
from tortoise.contrib.fastapi import register_tortoise
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from apps.users.api import router as user_router
from apps.projects.api import router as project_router
from apps.testmanage.api import router as test_router
from apps.testplan.api import router as plan_router
from apps.runner.api import router as runenr_router
from apps.crontab.api import router as cron_router

app = FastAPI(
    title="Web测试平台接口文档",
    description="FastApi",
    version="0.0.1",
    docs_url=None,
    redoc_url=None,  # 设置 ReDoc 文档的路径
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="xx",
        # oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url='/static/swagger/swagger-ui-bundle.js',
        swagger_css_url='/static/swagger/swagger-ui.css',
        swagger_favicon_url='/static/swagger/img.png',
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/swagger/redoc.standalone.js",
    )


register_tortoise(app, config=settings.TORTOISE_ORM, modules={'models': ['models']})

# 注册路由
app.include_router(user_router)
app.include_router(project_router)
app.include_router(test_router)
app.include_router(plan_router)
app.include_router(runenr_router)
app.include_router(cron_router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
