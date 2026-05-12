from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query

from core.dependency import AuthControl
from models.user import User
from models.enums import TransactionType
from controllers.transaction import transaction_controller
from controllers.ledger import ledger_controller
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut, TransactionSummary
from schemas.base import Success, Fail, SuccessExtra


router = APIRouter()


@router.post('', summary='创建交易记录')
async def create_transaction(
    obj_in: TransactionCreate,
    user: User = Depends(AuthControl.is_authed),
):
    ledger = await ledger_controller.get(id=obj_in.ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='账本不存在')
    
    tx = await transaction_controller.create(obj_in)
    return Success(data=await tx.to_dict())


@router.get('', summary='交易记录列表')
async def list_transactions(
    ledger_id: int = Query(..., description='账本ID'),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tx_type: Optional[int] = Query(None, alias='type', description='类型: 1=收入, 2=支出'),
    category_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user: User = Depends(AuthControl.is_authed),
):
    ledger = await ledger_controller.get(id=ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='账本不存在')
    
    type_enum = TransactionType(tx_type) if tx_type else None
    total, transactions = await transaction_controller.list_by_ledger(
        ledger_id, page, page_size, type_enum, category_id, start_date, end_date
    )
    data = [await t.to_dict() for t in transactions]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get('/summary', summary='收支汇总')
async def get_summary(
    ledger_id: int = Query(...),
    tx_type: Optional[int] = Query(None, alias='type'),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user: User = Depends(AuthControl.is_authed),
):
    ledger = await ledger_controller.get(id=ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='账本不存在')
    
    type_enum = TransactionType(tx_type) if tx_type else None
    summary = await transaction_controller.summary(ledger_id, type_enum, start_date, end_date)
    return Success(data=summary)


@router.get('/{transaction_id}', summary='交易记录详情')
async def get_transaction(transaction_id: int, user: User = Depends(AuthControl.is_authed)):
    tx = await transaction_controller.get(id=transaction_id)
    if not tx:
        return Fail(msg='记录不存在')
    
    ledger = await ledger_controller.get(id=tx.ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='记录不存在')
    
    return Success(data=await tx.to_dict())


@router.put('/{transaction_id}', summary='更新交易记录')
async def update_transaction(
    transaction_id: int,
    obj_in: TransactionUpdate,
    user: User = Depends(AuthControl.is_authed),
):
    tx = await transaction_controller.get(id=transaction_id)
    if not tx:
        return Fail(msg='记录不存在')
    
    ledger = await ledger_controller.get(id=tx.ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='记录不存在')
    
    tx = await transaction_controller.update(transaction_id, obj_in)
    return Success(data=await tx.to_dict())


@router.delete('/{transaction_id}', summary='删除交易记录')
async def delete_transaction(transaction_id: int, user: User = Depends(AuthControl.is_authed)):
    tx = await transaction_controller.get(id=transaction_id)
    if not tx:
        return Fail(msg='记录不存在')
    
    ledger = await ledger_controller.get(id=tx.ledger_id)
    if not ledger or ledger.user_id != user.user_id:
        return Fail(msg='记录不存在')
    
    await transaction_controller.remove(transaction_id)
    return Success(msg='Deleted Successfully')
