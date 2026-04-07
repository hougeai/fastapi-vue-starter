"""
AI-Practice Backend Service
Copyright (c) 2025 AI-Practice. All rights reserved.

This software contains proprietary information of AI-Practice.
Unauthorized copying, distribution or use of this software is strictly prohibited.
"""

import uvicorn
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from tortoise import Tortoise
from core.init_app import init_data, make_middlewares, register_exceptions, register_routers
from core.config import settings
from core.log import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger.log(record.levelno, record.getMessage(), exc_info=record.exc_info)


# 将uvicorn日志重定向到logger
for name in ('uvicorn', 'uvicorn.access'):
    log = logging.getLogger(name)
    log.handlers = [InterceptHandler()]
    log.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 应用启动前的操作
    await init_data(app)
    # 2. yield 表示应用正常运行阶段
    yield
    await Tortoise.close_connections()


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,  # 设置 API 文档的标题
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url='/openapi.json',  # OpenAPI (前身是 Swagger) 文档，包含了 API 的所有规范，FastAPI 自动生成的 API 文档的访问端点
        docs_url=None,  # 禁用默认的 Swagger UI（否则无法自定义）
        middleware=make_middlewares(),  # 调用这个函数获取中间件列表
        lifespan=lifespan,  # 传递函数本身作为引用
    )
    static_dir = BASE_DIR / 'static'
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')

    @app.get('/docs', include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + ' - Swagger UI',
            swagger_js_url='/static/swagger/swagger-ui-bundle.js',
            swagger_css_url='/static/swagger/swagger-ui.css',
            swagger_favicon_url='/static/swagger/favicon-32x32.png',  # 可选
        )

    register_exceptions(app)  # 定义的异常都会以 JSONResponse 的形式返回错误响应
    register_routers(app)
    return app


app = create_app()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=settings.BACK_END_PORT, reload=False, log_level='info', log_config=None)
