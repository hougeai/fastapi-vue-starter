from datetime import datetime, timezone
from typing import List, Optional
from fastapi.routing import APIRoute
from fastapi.exceptions import HTTPException

from core.security import get_password_hash, verify_password
from models.user import (
    User,
    Role,
    Api,
    Menu,
    RoleMenu,
    RoleApi,
)
from schemas.user import (
    UserCreate,
    UserUpdate,
    RoleCreate,
    RoleUpdate,
    ApiCreate,
    ApiUpdate,
    MenuCreate,
    MenuUpdate,
)
from schemas.login import PhoneLogin
from .crud import CRUDBase


# user controller：通过继承 CRUDBase 获得基础的 CRUD 操作
class UserController(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    async def get_by_user_id(self, user_id: str):
        return await self.model.filter(user_id=user_id).first()

    async def get_by_email(self, email: str, is_del: bool = False) -> Optional[User]:
        return await self.model.filter(email=email, is_del=is_del).first()

    async def get_by_phone(self, phone: str, is_del: bool = False) -> Optional[User]:
        return await self.model.filter(phone=phone, is_del=is_del).first()

    async def create_user(self, obj_in: UserCreate) -> User:
        if obj_in.password:
            obj_in.password = get_password_hash(password=obj_in.password)
        obj = await self.create(obj_in)
        return obj

    async def update_last_login(self, user_id: str) -> None:
        user = await self.get_by_user_id(user_id)
        user.last_login = datetime.now(timezone.utc)
        await user.save()

    async def authenticate(self, request: PhoneLogin) -> Optional[User]:
        user = await self.model.filter(phone=request.phone).first()
        if not user:
            raise HTTPException(status_code=400, detail='邮箱未注册！')
        verified = verify_password(request.password, user.password)
        if not verified:
            raise HTTPException(status_code=400, detail='密码错误!')
        if not user.is_active:
            raise HTTPException(status_code=400, detail='用户已被禁用！')
        if user.is_del:
            raise HTTPException(status_code=400, detail='用户已注销，请重新注册！')
        return user


user_controller = UserController()


# role controller
class RoleController(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(model=Role)

    async def is_exist(self, name: str) -> bool:
        return await self.model.filter(name=name).exists()

    async def update_roles(self, role: Role, menu_ids: List[int], api_infos: List[dict]) -> None:
        # 清除现有的角色菜单关联
        await RoleMenu.filter(role_id=role.id).delete()

        # 添加新的角色菜单关联
        role_menu_objects = [RoleMenu(role_id=role.id, menu_id=menu_id) for menu_id in menu_ids]
        if role_menu_objects:
            await RoleMenu.bulk_create(role_menu_objects)

        # 清除现有的角色API关联
        await RoleApi.filter(role_id=role.id).delete()

        # 添加新的角色API关联
        role_api_objects = []
        for item in api_infos:
            api_obj = await Api.filter(path=item.get('path'), method=item.get('method')).first()
            if api_obj:
                role_api_objects.append(RoleApi(role_id=role.id, api_id=api_obj.id))

        if role_api_objects:
            await RoleApi.bulk_create(role_api_objects)


role_controller = RoleController()


# api controller
class ApiController(CRUDBase[Api, ApiCreate, ApiUpdate]):
    def __init__(self):
        super().__init__(model=Api)

    async def refresh_api(self, app=None):
        if not app:
            raise ValueError('FastAPI instance must be provided')
        # 1. 获取应用中所有需要鉴权的路由
        all_api_list = []
        for route in app.routes:
            # 只更新有鉴权的API(例子： APIRoute(path='/api/v1/role/list', name='list_role', methods=['GET']))
            if isinstance(route, APIRoute) and len(route.dependencies) > 0:
                all_api_list.append((list(route.methods)[0], route.path_format))
        # 2. 数据库中存在，但应用中不存在的API
        delete_api = []
        for api in await Api.all():
            if (api.method, api.path) not in all_api_list:
                delete_api.append((api.method, api.path))
        for item in delete_api:
            method, path = item
            await Api.filter(method=method, path=path).delete()
        # 3. 应用中存在，数据库不存在：更新或创建API记录
        for route in app.routes:
            if isinstance(route, APIRoute) and len(route.dependencies) > 0:
                method = list(route.methods)[0]
                path = route.path_format
                summary = route.summary
                tags = list(route.tags)[0]
                api_obj = await Api.filter(method=method, path=path).first()
                # 存在则更新，不存在则创建
                if api_obj:
                    # update_from_dict 是 Tortoise ORM 的 Model 类中的一个内置方法
                    await api_obj.update_from_dict(dict(method=method, path=path, summary=summary, tags=tags)).save()
                else:
                    # 使用 ** 解包字典
                    await Api.create(**dict(method=method, path=path, summary=summary, tags=tags))


api_controller = ApiController()


# menu controller
class MenuController(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    def __init__(self):
        super().__init__(model=Menu)

    async def get_by_menu_path(self, path: str) -> Optional[Menu]:
        return await self.model.filter(path=path).first()


menu_controller = MenuController()
