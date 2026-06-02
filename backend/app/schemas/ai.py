from pydantic import BaseModel, Field
from typing import Optional


class AiParseTextRequest(BaseModel):
    text: str = Field(..., description='自然语言文本')
    ledger_id: int = Field(..., description='账本ID')


class AiParseVoiceRequest(BaseModel):
    ledger_id: int = Field(..., description='账本ID')


class AiParseImageRequest(BaseModel):
    ledger_id: int = Field(..., description='账本ID')


class AiParsedTransaction(BaseModel):
    tx_type: int = Field(..., description='类型: 1=收入, 2=支出')
    amount: float = Field(..., description='金额')
    category: str = Field(default='', description='类别名称')
    remark: str = Field(default='', description='备注')
    tx_date: str = Field(..., description='交易日期 YYYY-MM-DD')


class AiVoiceParsedTransaction(BaseModel):
    transcript: str = Field(default='', description='语音识别文本')
    parsed: Optional[AiParsedTransaction] = Field(default=None, description='解析结果')
