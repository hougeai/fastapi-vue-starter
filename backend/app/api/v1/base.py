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
from schemas.login import JWTPayload, JWTOut, EmailLogin, VerifyCodeRequest, RegisterRequest
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


@router.post('/email_login', summary='邮箱登录')
async def email_login(request: EmailLogin):
    user = await user_controller.authenticate(request)
    await user_controller.update_last_login(user.user_id)
    return generate_token_response(user, remember=request.remember)


# 用户邮箱注册相关API
@router.post('/verifycode', summary='发送验证码')
async def send_verify_code(request: VerifyCodeRequest):
    # 检查正常用户中邮箱是否已注册，注销用户可以继续用这个邮箱
    user = await user_controller.get_by_email(request.email, is_del=False)
    if user:
        return Fail(msg='邮箱已注册')
    # 发送验证码
    success, msg = await code_manager.generate_code(request.email)
    if not success:
        return Fail(msg=msg)
    return Success(msg=msg)


@router.post('/register', summary='用户注册')
async def register(request: RegisterRequest):
    # 验证验证码
    success, msg = await code_manager.verify_code(request.email, request.verification_code)
    if not success:
        return Fail(msg=msg)
    # 发送验证码时已验证过邮箱，先查询是否是is_del；如果不存在user说明是新用户，存在则是注销用户，需要恢复
    user = await user_controller.get_by_email(request.email, is_del=True)
    if not user:
        obj = UserCreate(
            user_name=request.user_name or request.email.split('@')[0],
            email=request.email,
            password=request.password,
            inviter_id=request.inviter_id,
        )
        user = await user_controller.create_user(obj)
    else:
        from core.security import get_password_hash
        await user_controller.update(
            id=user.id,
            obj_in={'is_del': False, 'user_name': request.user_name or request.email.split('@')[0], 'password': get_password_hash(request.password)},
        )
    return Success(msg='注册成功')


@router.post('/forgot_password', summary='忘记密码')
async def forgot_password(request: VerifyCodeRequest):
    user = await user_controller.get_by_email(request.email)
    if not user:
        return Fail(msg='邮箱未注册')
    # 使用Redis管理器生成重置令牌并发送重置密码链接
    success, msg = await code_manager.generate_reset_token(request.email)
    if not success:
        return Fail(msg=msg)
    return Success(msg=msg)
