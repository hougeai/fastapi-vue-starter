import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request
from core.config import settings
from core.background import CTX_USER_ID
from core.dependency import DependAuth
from core.security import create_token
from core.verifycode import RedisManager
from controllers import user_controller
from models.user import Role, Api, Menu, RoleApi, RoleMenu
from schemas.base import Fail, Success
from schemas.login import JWTPayload, JWTOut, PhoneLogin, PhoneRegister
from schemas.user import UserCreate

router = APIRouter()
code_manager = RedisManager()


def generate_token_response(user, remember: bool = False):
    # 生成过期时间
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_expire = datetime.now(timezone.utc) + access_token_expires
    refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_expire = datetime.now(timezone.utc) + refresh_token_expires
    # 生成 jwt token；字段id exp必须的，其它不宜过多
    data = JWTOut(
        access_token=create_token(
            data=JWTPayload(
                user_id=user.user_id,
                exp=access_expire,
            )
        ),
        user_id=user.user_id,
    )
    refresh_token = create_token(data=JWTPayload(user_id=user.user_id, exp=refresh_expire))
    # 将 Pydantic 模型的所有字段转换为 Python 字典
    response = Success(data=data.model_dump())
    # 放在cookie中，前端 JavaScript 无法访问，localStorage 中不保存
    if remember:
        max_age = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    else:
        max_age = None
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=False,
        max_age=max_age,
    )
    return response


@router.post('/refresh_token', summary='刷新token')
async def refresh_token(request: Request):
    # 从cookie中获取refresh_token
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return Fail(msg='refresh token不存在')
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': True},
        )
        # 检查是否有用户信息
        if not payload.get('user_id', ''):
            return Fail(msg='无效的refresh token')
        user_id = payload['user_id']
        user = await user_controller.get_by_user_id(user_id)
        if not user:
            return Fail(msg='用户不存在')

        # 生成新的access token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_expire = datetime.now(timezone.utc) + access_token_expires

        data = JWTOut(
            access_token=create_token(
                data=JWTPayload(
                    user_id=user.user_id,
                    exp=access_expire,
                )
            ),
            user_id=user.user_id,
        )
        return Success(data=data.model_dump())
    except jwt.ExpiredSignatureError:
        return Fail(msg='refresh token已过期')
    except jwt.InvalidTokenError:
        return Fail(msg='无效的refresh token')
    except Exception as e:
        return Fail(msg=f'token验证失败: {str(e)}')


@router.get('/userinfo', summary='查看用户信息', dependencies=[DependAuth])
async def get_userinfo():
    user_id = CTX_USER_ID.get()  # 保证用户身份的一致性；AuthControl中set
    user_obj = await user_controller.get_by_user_id(user_id)
    if not user_obj:
        return Fail(msg='用户不存在')
    data = await user_obj.to_dict(exclude_fields=['password', 'id'])
    # 获取用户角色信息
    role = await Role.filter(id=user_obj.role_id).first()
    data['role_name'] = role.name if role else ''
    data['role_desc'] = role.desc if role else ''
    # 获取用户角色到期信息
    data['role_expire'] = datetime.now(timezone.utc).isoformat()
    # if role.id > 3:
    #     exist_orders = await UserOrder.filter(user_id=user_id, role_id=role.id, is_expired=False).order_by('-expire_at')
    #     if exist_orders:
    #         data['role_expire'] = (exist_orders[0].expire_at).isoformat()
    return Success(data=data)


@router.get('/usermenu', summary='查看用户菜单', dependencies=[DependAuth])
async def get_user_menu():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get_by_user_id(user_id)
    if not user_obj:
        return Fail(msg='用户不存在')
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = await Menu.all()
    else:
        role_menus = await RoleMenu.filter(role_id=user_obj.role_id).all()
        menu_ids = [role_menu.menu_id for role_menu in role_menus]
        menus = await Menu.filter(id__in=menu_ids).all()

    parent_menus: list[Menu] = []
    for menu in menus:
        if menu.parent_id == 0:
            parent_menus.append(menu)
    res = []
    for parent_menu in parent_menus:
        parent_menu_dict = await parent_menu.to_dict()
        parent_menu_dict['children'] = []
        for menu in menus:
            if menu.parent_id == parent_menu.id:
                parent_menu_dict['children'].append(await menu.to_dict())
        res.append(parent_menu_dict)
    return Success(data=res)


@router.get('/userapi', summary='查看用户API', dependencies=[DependAuth])
async def get_user_api():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get_by_user_id(user_id)
    if not user_obj:
        return Fail(msg='用户不存在')
    if user_obj.is_superuser:
        api_objs: list[Api] = await Api.all()
        apis = [api.method.lower() + api.path for api in api_objs]
        return Success(data=apis)
    role_apis = await RoleApi.filter(role_id=user_obj.role_id).all()
    api_ids = [ra.api_id for ra in role_apis]
    api_objs = await Api.filter(id__in=api_ids).all()
    apis = [api.method.lower() + api.path for api in api_objs]
    return Success(data=apis)


# 手机号注册相关
@router.post('/phone_code', summary='发送验证码')
async def send_phone_code(request: PhoneRegister):
    # 发送验证码
    success, msg = await code_manager.generate_phone_code(request.phone)
    if not success:
        return Fail(msg=msg)
    return Success(msg=msg)


@router.post('/phone_login', summary='手机号登录')
async def phone_login(request: PhoneLogin):
    # 验证用户名和密码
    user = await user_controller.authenticate(request)
    return generate_token_response(user, request.remember)


@router.post('/phone_register', summary='手机号注册')
async def phone_register(request: PhoneRegister):
    # 验证验证码
    success, msg = await code_manager.verify_phone_code(request.phone, request.code)
    if not success:
        return Fail(msg=msg)
    # 验证手机号是否已注册
    user = await user_controller.get_by_phone(request.phone)
    if not user:
        # 注册新用户
        obj = UserCreate(
            user_name='手机注册用户',
            phone=request.phone,
            inviter_id=request.inviter_id,
        )
        user = await user_controller.create_user(obj)
    if user.is_del:
        # 注销用户恢复
        await user_controller.update(id=user.id, obj_in={'is_del': False})
    # 更新最后登录时间
    await user_controller.update_last_login(user.user_id)
    return generate_token_response(user, request.remember)
