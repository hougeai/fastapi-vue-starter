import shutil
from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.expressions import Q
from api import api_router
from models.user import Api, Role, RoleApi
from schemas.user import UserCreate
from controllers import api_controller, user_controller
from .exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from .log import logger
from .config import settings
from .middlewares import BackGroundTaskMiddleware, HttpAuditLogMiddleware


def make_middlewares():
    allowed_origins = [
        settings.ADMIN_FE_URL,
        settings.USER_FE_URL,
        'http://localhost:8078',
        'http://127.0.0.1:8078',
        'http://localhost:8087',
        'http://localhost:8088',
    ]
    allowed_origins = [origin for origin in allowed_origins if origin]

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        ),
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=['GET', 'POST', 'PUT', 'DELETE'],
            exclude_paths=[
                '/docs',
                '/redoc',
                '/openapi.json',
                r'^/static/.*',
                r'^/$',
                '/favicon.ico',
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)


def register_routers(app: FastAPI):
    app.include_router(api_router, prefix='/api')


async def init_db():
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    try:
        await command.init_db(safe=True)  # 初始化数据库，safe=True 表示如果表已存在则跳过
    except FileExistsError:
        pass

    await command.init()  # 初始化 migrations 目录和配置
    try:
        await command.migrate()  # 根据模型变化生成迁移文件
    except AttributeError:
        # 如果获取不到历史记录，则重新初始化
        logger.warning('unable to retrieve model history from database, model history will be created from scratch')
        shutil.rmtree('migrations')  # 删除旧的迁移文件
        await command.init_db(safe=True)  # 重新初始化

    await command.upgrade(run_in_transaction=True)


async def init_apis(app: FastAPI):
    # 每次重启都要刷新api
    await api_controller.refresh_api(app)


async def init_roles():
    roles = await Role.exists()
    if not roles:
        init_roles = [
            ('超级管理员', '拥有系统所有权限，可管理所有用户和设置'),
            ('管理员', '拥有管理权限，可管理普通用户和部分设置'),
            ('免费会员', '基础用户权限，可使用核心功能'),
            ('VIP会员', 'VIP会员权限，可使用更多新功能，高峰期优先队列'),
        ]
        role_objs = [Role(name=n, desc=d) for n, d in init_roles]
        await Role.bulk_create(role_objs)

    # 分配所有API给超级管理员-先清空再重新赋值
    super_admin = await Role.get(name='超级管理员').first()
    await RoleApi.filter(role_id=super_admin.id).delete()
    all_apis = await Api.all()
    role_api_objects = [RoleApi(role_id=super_admin.id, api_id=api.id) for api in all_apis]
    await RoleApi.bulk_create(role_api_objects)

    # 为免费会员、VIP会员和SVIP会员分配基本API和用户信息更新API
    member_roles = await Role.filter(name__in=['免费会员', 'VIP会员']).all()
    basic_apis = await Api.filter(
        Q(method__in=['GET']) | Q(tags='基础模块') | Q(tags='产品模块') | Q(tags='音色模块') | Q(tags='直播间模块')
    )
    user_update_api = await Api.filter(method='POST', tags='用户模块', summary='更新用户')
    all_apis = list(basic_apis) + list(user_update_api)
    for role in member_roles:
        await RoleApi.filter(role_id=role.id).delete()
        role_api_objects = [RoleApi(role_id=role.id, api_id=api.id) for api in all_apis]
        await RoleApi.bulk_create(role_api_objects)


async def init_superuser():
    user = await user_controller.model.exists()
    if not user:
        await user_controller.create_user(
            UserCreate(
                user_id='1',
                user_name=settings.SUPER_ADMIN_NAME,
                password=settings.SUPER_ADMIN_PASSWORD,
                phone=settings.SUPER_ADMIN_PHONE,
                avatar='https://avatars.githubusercontent.com/u/23102037?s=96&v=4',
                is_active=True,
                role_id=1,
            )
        )


async def init_data(app: FastAPI):
    await init_db()
    await init_apis(app)
    await init_roles()
    await init_superuser()
