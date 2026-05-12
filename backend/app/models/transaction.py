from tortoise import fields
from .base import BaseModel, TimestampMixin
from .enums import TransactionType


# 交易记录表
class Transaction(BaseModel, TimestampMixin):
    ledger_id = fields.IntField(description='账本ID', index=True)
    tx_type = fields.IntEnumField(TransactionType, description='类型: 1=收入, 2=支出', index=True)
    amount = fields.DecimalField(max_digits=12, decimal_places=2, description='金额')
    category_id = fields.IntField(null=True, description='类别ID', index=True)
    remark = fields.CharField(max_length=500, null=True, description='备注')
    tx_date = fields.DateField(description='交易日期', index=True)

    class Meta:
        table = 'transaction'
