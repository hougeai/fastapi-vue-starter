from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field

from core.dependency import AuthControl
from models.user import User
from controllers.ai import parse_text, parse_voice, parse_image
from schemas.base import Success, Fail

router = APIRouter()


class ParseTextRequest(BaseModel):
    text: str = Field(..., description='自然语言文本')
    ledger_id: int = Field(..., description='账本ID')


@router.post('/parse_text', summary='自然语言解析为交易记录')
async def ai_parse_text(
    obj_in: ParseTextRequest,
    user: User = Depends(AuthControl.is_authed),
):
    result = await parse_text(obj_in.text, obj_in.ledger_id)
    if 'error' in result:
        return Fail(msg=result['error'])
    return Success(data=result['data'])


@router.post('/parse_voice', summary='语音解析为交易记录')
async def ai_parse_voice(
    ledger_id: int = Form(..., description='账本ID'),
    file: UploadFile = File(...),
    user: User = Depends(AuthControl.is_authed),
):
    result = await parse_voice(file, ledger_id)
    if 'error' in result:
        # 如果有识别文本但LLM解析失败，仍返回识别文本
        if 'data' in result and result['data'].get('transcript'):
            return Success(data=result['data'])
        return Fail(msg=result['error'])
    return Success(data=result['data'])


@router.post('/parse_image', summary='图片解析为交易记录')
async def ai_parse_image(
    ledger_id: int = Form(..., description='账本ID'),
    file: UploadFile = File(...),
    user: User = Depends(AuthControl.is_authed),
):
    result = await parse_image(file, ledger_id)
    if 'error' in result:
        return Fail(msg=result['error'])
    return Success(data=result.get('data', {}))
