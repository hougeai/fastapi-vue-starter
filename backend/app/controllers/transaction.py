from typing import Optional, Tuple, List
from datetime import date
from decimal import Decimal
from tortoise.expressions import Q
from models.transaction import Transaction
from models.enums import TransactionType
from schemas.transaction import TransactionCreate, TransactionUpdate
from .crud import CRUDBase


class TransactionController(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    def __init__(self):
        super().__init__(model=Transaction)

    async def list_by_ledger(
        self,
        ledger_id: int,
        page: int = 1,
        page_size: int = 20,
        tx_type: Optional[TransactionType] = None,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[int, List[Transaction]]:
        """按账本分页查询交易记录"""
        query = self.model.filter(ledger_id=ledger_id)
        
        if tx_type:
            query = query.filter(tx_type=tx_type.value)
        if category_id:
            query = query.filter(category_id=category_id)
        if start_date:
            query = query.filter(tx_date__gte=start_date)
        if end_date:
            query = query.filter(tx_date__lte=end_date)
        
        total = await query.count()
        results = await query.order_by('-tx_date', '-id').offset((page - 1) * page_size).limit(page_size).all()
        return total, results

    async def summary(
        self,
        ledger_id: int,
        tx_type: Optional[TransactionType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        """收支汇总统计"""
        query = self.model.filter(ledger_id=ledger_id)
        
        if start_date:
            query = query.filter(tx_date__gte=start_date)
        if end_date:
            query = query.filter(tx_date__lte=end_date)
        
        income = await query.filter(tx_type=TransactionType.INCOME.value).all()
        expense = await query.filter(tx_type=TransactionType.EXPENSE.value).all()
        
        total_income = sum(t.amount for t in income)
        total_expense = sum(t.amount for t in expense)
        
        return {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(total_income - total_expense),
            'count': len(income) + len(expense),
        }


transaction_controller = TransactionController()
