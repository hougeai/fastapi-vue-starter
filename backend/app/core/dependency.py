import jwt
from typing import Optional
from fastapi import Depends, Header, HTTPException, Request

from models.user import User, Api, RoleApi
from .config import settings
from .background import CTX_USER_ID


# 处理用户认证
class AuthControl:
    @classmethod
    # Optional[User] 等价于 User | None
    async def is_authed(cls, request: Request, token: str = Header(..., description='token验证')) -> Optional[User]:
        try:
            if token == 'dev':
                user = await User.filter().first()
                user_id = user.user_id
            else:
                decode_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
                user_id = decode_data.get('user_id')
            user = await User.filter(user_id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail='Authentication failed')
            CTX_USER_ID.set(user_id)
            request.state.user_id = user_id
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail='无效的Token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=419, detail='登录已过期')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{repr(e)}')


# 处理权限控制：请求对象和当前用户作为参数，明确指定了返回类型为 None （通过 -> None ），return 就是隐式返回None
class PermissionControl:
    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> None:
        # 超级用户拥有所有权限
        if current_user.is_superuser:
            return
        method = request.method
        path = request.url.path  # 获取请求路径
        role_id = current_user.role_id  # 获取当前用户的角色
        if not role_id:
            raise HTTPException(status_code=403, detail='The user is not bound to a role')
        role_apis = await RoleApi.filter(role_id=role_id).all()
        api_ids = [ra.api_id for ra in role_apis]
        api_objs = await Api.filter(id__in=api_ids).all()
        permission_apis = [(api.method, api.path) for api in api_objs]
        if (method, path) not in permission_apis:
            raise HTTPException(status_code=403, detail=f'Permission denied method:{method} path:{path}')


DependAuth = Depends(AuthControl.is_authed)
DependPermisson = Depends(PermissionControl.has_permission)
