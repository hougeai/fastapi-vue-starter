import json
import re
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send
from models.user import AuditLog
from .background import BgTasks, CTX_USER_ID


class SimpleBaseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def before_request(self, request: Request):
        return self.app

    async def after_request(self, request: Request):
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    async def before_request(self, request):
        await BgTasks.init_bg_tasks_obj()

    async def after_request(self, request):
        await BgTasks.execute_tasks()


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths
        self.audit_log_paths = ['/api/v1/auditlog/list']
        self.max_body_size = 1024 * 1024  # 1MB 响应体大小限制

    # 收集 URL 参数和请求体数据
    async def get_request_args(self, request: Request) -> dict:
        args = {}
        # 获取查询参数
        for key, value in request.query_params.items():
            args[key] = value

        # 获取请求体
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('content-type', '').lower()
            if 'multipart/form-data' in content_type:
                try:
                    # 不要在中间件中读取表单数据，否则后面请求将不会有数据了
                    # body = await request.form()
                    # 只记录内容类型
                    args['_content_type'] = 'multipart/form-data'
                except Exception:
                    pass
            else:
                try:
                    body = await request.json()
                    args.update(body)
                except json.JSONDecodeError:
                    pass

        return args

    # 处理响应体，限制大小，处理特殊路径
    async def get_response_body(self, request: Request, response: Response) -> Any:
        # 检查Content-Length
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > self.max_body_size:
            return {'code': 0, 'msg': 'Response too large to log', 'data': None}

        if hasattr(response, 'body'):
            body = response.body
        else:
            body_chunks = []
            async for chunk in response.body_iterator:
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(response.charset)
                body_chunks.append(chunk)

            response.body_iterator = self._async_iter(body_chunks)
            body = b''.join(body_chunks)

        if any(request.url.path.startswith(path) for path in self.audit_log_paths):
            try:
                data = self.lenient_json(body)
                # 只保留基本信息，去除详细的响应内容
                if isinstance(data, dict):
                    data.pop('response_body', None)
                    if 'data' in data and isinstance(data['data'], list):
                        for item in data['data']:
                            item.pop('response_body', None)
                return data
            except Exception:
                return None

        return self.lenient_json(body)

    def lenient_json(self, v: Any) -> Any:
        if isinstance(v, (str, bytes)):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                pass
        return v

    async def _async_iter(self, items: list[bytes]) -> AsyncGenerator[bytes, None]:
        for item in items:
            yield item

    # 日志记录：路径、状态码、方法；模块信息和接口描述；用户信息
    async def get_request_log(self, request: Request, response: Response) -> dict:
        """
        根据request和response对象获取对应的日志记录数据
        """
        data: dict = {'path': request.url.path, 'status': response.status_code, 'method': request.method}
        # 路由信息
        app: FastAPI = request.app
        for route in app.routes:
            if (
                isinstance(route, APIRoute)
                and route.path_regex.match(request.url.path)
                and request.method in route.methods
            ):
                data['module'] = ','.join(route.tags)
                data['summary'] = route.summary
        return data

    async def before_request(self, request: Request):
        request_args = await self.get_request_args(request)
        request.state.request_args = request_args

    async def after_request(self, request: Request, response: Response, process_time: int):
        if request.method in self.methods:
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return
            data: dict = await self.get_request_log(request=request, response=response)
            data['latency'] = process_time
            data['args'] = request.state.request_args
            data['body'] = await self.get_response_body(request, response)
            # 获取用户信息：Starlette 的 BaseHTTPMiddleware 在某些情况下会切换执行上下文/Task，导致 contextvars 丢失
            user_id = getattr(request.state, 'user_id', None) or CTX_USER_ID.get()
            data['user_id'] = user_id if user_id else '0'
            await AuditLog.create(**data)

        return response

    # dispatch 方法是中间件的主要入口点，在请求到达后，会调用此方法，记录请求处理时间
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time: datetime = datetime.now()
        await self.before_request(request)
        response = await call_next(request)
        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)
        await self.after_request(request, response, process_time)
        return response
