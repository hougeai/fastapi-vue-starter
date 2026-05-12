from typing import Optional
from pydantic import BaseModel, Field
from datetime import date


class TransactionCreate(BaseModel):
    ledger_id: int = Field(..., description='账本ID')
    tx_type: int = Field(..., description='类型: 1=收入, 2=支出')
    amount: float = Field(..., description='金额')
    category_id: Optional[int] = Field(default=None, description='类别ID')
    remark: Optional[str] = Field(default=None, description='备注')
    tx_date: date = Field(..., description='交易日期')


class TransactionUpdate(BaseModel):
    id: int
    tx_type: Optional[int] = Field(default=None, description='类型')
    amount: Optional[float] = Field(default=None, description='金额')
    category_id: Optional[int] = Field(default=None, description='类别ID')
    remark: Optional[str] = Field(default=None, description='备注')
    tx_date: Optional[date] = Field(default=None, description='交易日期')


class TransactionOut(BaseModel):
    id: int
    ledger_id: int
    tx_type: int
    amount: float
    category_id: Optional[int]
    remark: Optional[str]
    date: str
    create_at: str
    update_at: str

    model_config = {'from_attributes': True}


class TransactionSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    count: int
