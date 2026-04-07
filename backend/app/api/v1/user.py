from fastapi import APIRouter, Query
from tortoise.expressions import Q
from controllers import user_controller
from schemas.base import Fail, Success, SuccessExtra
from schemas.user import UserUpdate

router = APIRouter()


@router.get('/list', summary='查看用户列表')
async def list_user(
    page: int = Query(1, description='页码'),
    page_size: int = Query(10, description='每页数量'),
    user_name: str = Query('', description='用户名称，用于搜索'),
    user_id: str = Query('', description='用户ID，用于搜索'),
):
    q = Q()
    if user_name:
        q &= Q(user_name__contains=user_name)  # SQL: WHERE user_name LIKE '%xxx%'；user_name=user_name 精确匹配
    if user_id:
        q &= Q(user_id=user_id)
    # 当前页码 每页显示数量；返回的是总数和当前页数据列表
    total, user_objs = await user_controller.list(page=page, page_size=page_size, search=q, order=['id'])
    # to_dict在model中定义
    data = [await obj.to_dict(m2m=True, exclude_fields=['password']) for obj in user_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/get', summary='查看用户')
async def get_user(
    user_id: str = Query(..., description='用户ID'),
):
    user_obj = await user_controller.get_by_user_id(user_id=user_id)
    user_dict = await user_obj.to_dict(exclude_fields=['password'])
    return Success(data=user_dict)


@router.post('/update', summary='更新用户')
async def update_user(
    user_in: UserUpdate,
):
    user = await user_controller.get_by_user_id(user_id=user_in.user_id)
    if not user:
        return Fail(code=400, msg='用户不存在')
    await user_controller.update(id=user.id, obj_in=user_in)
    return Success(msg='Updated Successfully')


@router.delete('/delete', summary='删除用户')
async def delete_user(
    user_id: int = Query(..., description='用户ID'),
):
    await user_controller.remove(id=user_id)
    return Success(msg='Deleted Successfully')
