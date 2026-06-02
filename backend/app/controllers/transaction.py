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

    async def category_summary(
        self,
        ledger_id: int,
        tx_type: Optional[TransactionType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """按类别汇总统计"""
        from models.ledger import Category
        query = self.model.filter(ledger_id=ledger_id)

        if tx_type:
            query = query.filter(tx_type=tx_type.value)
        if start_date:
            query = query.filter(tx_date__gte=start_date)
        if end_date:
            query = query.filter(tx_date__lte=end_date)

        transactions = await query.all()

        # 按 category_id 分组汇总
        category_map = {}
        for t in transactions:
            cat_id = t.category_id or 0
            if cat_id not in category_map:
                category_map[cat_id] = {'amount': 0, 'count': 0, 'tx_type': t.tx_type}
            category_map[cat_id]['amount'] += t.amount
            category_map[cat_id]['count'] += 1

        # 获取类别名称
        result = []
        for cat_id, info in category_map.items():
            if cat_id and cat_id > 0:
                cat = await Category.filter(id=cat_id).first()
                cat_name = cat.name if cat else '未分类'
            else:
                cat_name = '未分类'
            result.append({
                'category_id': cat_id,
                'category_name': cat_name,
                'tx_type': info['tx_type'],
                'amount': float(info['amount']),
                'count': info['count'],
            })

        # 按金额降序
        result.sort(key=lambda x: x['amount'], reverse=True)
        return result


transaction_controller = TransactionController()
