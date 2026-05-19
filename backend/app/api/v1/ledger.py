from typing import Optional
from fastapi import APIRouter, Depends, Query

from core.dependency import AuthControl
from models.user import User
from models.enums import TransactionType
from controllers.ledger import ledger_controller, category_controller, ledger_template_controller
from schemas.ledger import LedgerCreate, LedgerUpdate, CategoryCreate, CategoryUpdate, LedgerTemplateCreate, LedgerTemplateUpdate
from schemas.base import Success, Fail


router = APIRouter()


# ============ LedgerTemplate 账本模板 ============
@router.get('/template', summary='获取账本模板列表')
async def list_templates():
    """获取所有账本模板"""
    templates = await ledger_template_controller.model.all()
    data = [await t.to_dict() for t in templates]
    return Success(data=data)


@router.post('/template', summary='创建账本模板（管理员）')
async def create_template(
    obj_in: LedgerTemplateCreate,
    user: User = Depends(AuthControl.is_authed),
):
    """创建账本模板"""
    if not user.is_superuser:
        return Fail(msg='Admin only')
    template = await ledger_template_controller.create(obj_in)
    return Success(data=await template.to_dict())


@router.post('/template/{template_id}/create', summary='从模板创建账本')
async def create_ledger_from_template(
    template_id: int,
    name: str = Query(..., description='账本名称'),
    description: Optional[str] = Query(None, description='账本描述'),
    user: User = Depends(AuthControl.is_authed),
):
    """从模板创建账本，同时创建预设类别"""
    try:
        ledger, categories = await ledger_controller.create_from_template(
            user.user_id, template_id, name, description
        )
        return Success(data={
            'ledger': await ledger.to_dict(),
            'categories': [await c.to_dict() for c in categories],
        })
    except ValueError as e:
        return Fail(msg=str(e))


# ============ Category 类别（放在 ledger/{ledger_id} 之前，避免路由冲突） ============
@router.post('/category', summary='创建类别')
async def create_category(
    obj_in: CategoryCreate,
    user: User = Depends(AuthControl.is_authed),
):
    # 重名检查
    if await category_controller.exists_by_name(user.user_id, obj_in.name):
        return Fail(msg='Category name already exists')
    category = await category_controller.create_for_user(user.user_id, obj_in)
    return Success(data=await category.to_dict())


@router.get('/category', summary='获取类别列表')
async def list_categories(
    tx_type: Optional[int] = Query(None, alias='type', description='类型: 1=收入, 2=支出'),
    user: User = Depends(AuthControl.is_authed),
):
    type_enum = TransactionType(tx_type) if tx_type else None
    categories = await category_controller.get_by_user(user.user_id, type_enum)
    data = [await c.to_dict() for c in categories]
    return Success(data=data)


@router.put('/category/{category_id}', summary='更新类别')
async def update_category(
    category_id: int,
    obj_in: CategoryUpdate,
    user: User = Depends(AuthControl.is_authed),
):
    category = await category_controller.get(id=category_id)
    if not category:
        return Fail(msg='Category not found')
    
    # 系统预设类别只有管理员才能修改（此处简化处理：不允许修改）
    if category.is_system and category.user_id is None:
        return Fail(msg='Cannot modify system category')
    
    # 用户只能修改自己的类别
    if category.user_id != user.user_id:
        return Fail(msg='No permission to modify this category')
    
    # 重名检查
    if obj_in.name and await category_controller.exists_by_name(user.user_id, obj_in.name, exclude_id=category_id):
        return Fail(msg='Category name already exists')
    
    category = await category_controller.update(category_id, obj_in)
    return Success(data=await category.to_dict())


@router.delete('/category/{category_id}', summary='删除类别')
async def delete_category(
    category_id: int,
    user: User = Depends(AuthControl.is_authed),
):
    category = await category_controller.get(id=category_id)
    if not category:
        return Fail(msg='Category not found')
    
    # 系统预设类别不能删除
    if category.is_system and category.user_id is None:
        return Fail(msg='Cannot delete system category')
    
    # 用户只能删除自己的类别
    if category.user_id != user.user_id:
        return Fail(msg='No permission to delete this category')
    
    await category_controller.remove(category_id)
    return Success(msg='Deleted Successfully')


@router.get('/category/system', summary='获取系统预设类别')
async def list_system_categories(
    tx_type: Optional[int] = Query(None, alias='type', description='类型: 1=收入, 2=支出'),
):
    """获取所有系统预设类别"""
    type_enum = TransactionType(tx_type) if tx_type else None
    categories = await category_controller.get_system_categories(type_enum)
    data = [await c.to_dict() for c in categories]
    return Success(data=data)


# ============ Ledger 账本 ============
@router.post('', summary='创建账本')
async def create_ledger(
    obj_in: LedgerCreate,
    user: User = Depends(AuthControl.is_authed),
):
    ledger = await ledger_controller.create_for_user(user.user_id, obj_in)
    return Success(data=await ledger.to_dict())


@router.get('', summary='获取账本列表')
async def list_ledgers(user: User = Depends(AuthControl.is_authed)):
    ledgers = await ledger_controller.get_by_user(user.user_id)
    data = [await l.to_dict() for l in ledgers]
    return Success(data=data)


@router.get('/{ledger_id}', summary='获取账本详情')
async def get_ledger(ledger_id: int, user: User = Depends(AuthControl.is_authed)):
    ledger = await ledger_controller.get(id=ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='Ledger not found')
    return Success(data=await ledger.to_dict())


@router.put('/{ledger_id}', summary='更新账本')
async def update_ledger(
    ledger_id: int,
    obj_in: LedgerUpdate,
    user: User = Depends(AuthControl.is_authed),
):
    ledger = await ledger_controller.get(id=ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='Ledger not found')
    ledger = await ledger_controller.update(ledger_id, obj_in)
    return Success(data=await ledger.to_dict())


@router.delete('/{ledger_id}', summary='删除账本')
async def delete_ledger(ledger_id: int, user: User = Depends(AuthControl.is_authed)):
    ledger = await ledger_controller.get(id=ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='账本不存在')
    await ledger_controller.remove(ledger_id)
    return Success(msg='Deleted Successfully')


@router.post('/{ledger_id}/default', summary='设为默认账本')
async def set_default_ledger(ledger_id: int, user: User = Depends(AuthControl.is_authed)):
    ledger = await ledger_controller.get(id=ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='Ledger not found')
    ledger = await ledger_controller.set_default(ledger_id, user.user_id)
    return Success(data=await ledger.to_dict())
