import json
import re
from datetime import date, datetime
from core.llm import unillm
from core.log import logger

# 通用规则（文本和图片共用）
_COMMON_RULES = """返回格式要求（严格 JSON，不要其他文字）：
{
  "tx_type": 1或2,
  "amount": 数字,
  "category": "类别名称",
  "remark": "备注",
  "tx_date": "YYYY-MM-DD"
}

规则：
- 收入 tx_type=1，支出 tx_type=2
- 类别从以下选项中选择最匹配的：
  收入类：工资、奖金、投资收益、兼职、红包、退款、其他收入
  支出类：餐饮、交通、购物、娱乐、房租、医疗、教育、通讯、服装、日用品、社交、旅行、宠物、机票、住宿、门票、门诊、住院、药品、检查、其他支出
- 如果没有明确日期，使用今天的日期
- 金额只写数字，不带货币符号
- remark 简短概括用途
- 只返回 JSON，不要任何解释文字

示例：
输入："今天午饭花了30元"
输出：{"tx_type": 2, "amount": 30, "category": "餐饮", "remark": "午饭", "tx_date": "2025-06-02"}

输入："6月工资到账15000"
输出：{"tx_type": 1, "amount": 15000, "category": "工资", "remark": "6月工资", "tx_date": "2025-06-02"}

输入："打车去公司25块"
输出：{"tx_type": 2, "amount": 25, "category": "交通", "remark": "打车", "tx_date": "2025-06-02"}"""

# 文本输入提示词
SYSTEM_PROMPT = "你是一个记账助手。用户会用自然语言描述一笔收支，你需要将其解析为结构化的 JSON 数据。\n\n" + _COMMON_RULES

# 图片识别提示词
IMAGE_PROMPT = (
    "你是一个记账助手。用户会上传一张小票、账单或收据的图片，你需要识别图片中的交易信息并解析为结构化的 JSON 数据。\n\n"
    "补充规则：\n"
    "- 除非是工资条等收入凭证，否则默认为支出 tx_type=2\n"
    "- amount 取小票上的总金额（实付金额）\n"
    "- remark 填写商户名称或消费内容（如\"海底捞\"、\"中石化加油\"）\n"
    "- tx_date 取小票上的日期，如果没有则使用今天的日期\n"
    "- 如果图片模糊无法识别关键信息，返回空 JSON: {}\n\n"
) + _COMMON_RULES


def _get_today_str() -> str:
    """每次请求时动态获取今天的日期"""
    return date.today().strftime('%Y-%m-%d')


async def parse_text(text: str, ledger_id: int) -> dict:
    """
    自然语言解析为交易记录
    """
    today_str = _get_today_str()
    logger.info(f'[AI] parse_text 请求: text="{text}", ledger_id={ledger_id}, today={today_str}')

    # 替换提示词中的示例日期，并在用户消息中明确告知今天日期
    prompt = SYSTEM_PROMPT.replace('2025-06-02', today_str)
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': f'今天是{today_str}。{text}'},
    ]

    try:
        raw = await unillm(messages, temperature=0.1)
        logger.info(f'[AI] parse_text LLM 原始返回: {raw[:500] if raw else "空"}')

        if not raw:
            logger.warning('[AI] parse_text LLM 返回为空')
            return {'error': 'AI 服务暂不可用，请稍后重试'}

        # 提取 JSON（兼容 LLM 返回 ```json ... ``` 格式）
        json_str = raw.strip()
        json_match = re.search(r'\{[^}]+\}', json_str, re.DOTALL)
        if json_match:
            json_str = json_match.group()

        result = json.loads(json_str)

        # 校验必要字段
        if 'tx_type' not in result or 'amount' not in result:
            logger.warning(f'[AI] parse_text 缺少必要字段: {result}')
            return {'error': '无法识别交易信息，请手动输入'}

        # 校验 tx_type
        if result['tx_type'] not in (1, 2):
            logger.warning(f'[AI] parse_text tx_type 异常: {result}')
            return {'error': '无法确定收支类型，请手动输入'}

        # 校验金额
        try:
            result['amount'] = float(result['amount'])
            if result['amount'] <= 0:
                return {'error': '金额必须大于0，请手动输入'}
        except (ValueError, TypeError):
            return {'error': '金额格式错误，请手动输入'}

        # 补全可选字段
        result.setdefault('category', '')
        result.setdefault('remark', '')
        result.setdefault('tx_date', today_str)

        # 校验日期格式
        try:
            datetime.strptime(result['tx_date'], '%Y-%m-%d')
        except ValueError:
            result['tx_date'] = today_str

        logger.info(f'[AI] parse_text 解析成功: {result}')
        return {'data': result}

    except json.JSONDecodeError:
        logger.warning(f'[AI] parse_text JSON 解析失败, 原始返回: {raw[:200]}')
        # 尝试让 LLM 重新解析一次
        retry_messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f'今天是{today_str}。{text}'},
            {'role': 'assistant', 'content': raw},
            {'role': 'user', 'content': '你的回复不是纯JSON格式。请严格只返回JSON，不要任何解释文字。'},
        ]
        retry_raw = await unillm(retry_messages, temperature=0.0)
        if retry_raw:
            logger.info(f'[AI] parse_text 重试 LLM 返回: {retry_raw[:300]}')
            try:
                retry_json = retry_raw.strip()
                retry_match = re.search(r'\{[^}]+\}', retry_json, re.DOTALL)
                if retry_match:
                    retry_json = retry_match.group()
                result = json.loads(retry_json)
                if 'tx_type' in result and 'amount' in result and result['tx_type'] in (1, 2):
                    try:
                        result['amount'] = float(result['amount'])
                    except (ValueError, TypeError):
                        pass
                    else:
                        result.setdefault('category', '')
                        result.setdefault('remark', '')
                        result.setdefault('tx_date', today_str)
                        try:
                            datetime.strptime(result['tx_date'], '%Y-%m-%d')
                        except ValueError:
                            result['tx_date'] = today_str
                        logger.info(f'[AI] parse_text 重试解析成功: {result}')
                        return {'data': result}
            except (json.JSONDecodeError, Exception):
                pass
        return {'error': 'AI 无法理解该描述，请换种说法或手动输入'}
    except Exception as e:
        logger.error(f'[AI] parse_text 异常: {e}', exc_info=True)
        return {'error': f'解析失败: {str(e)}'}


async def asr_voice(audio_file) -> dict:
    """
    语音识别（仅 ASR）：返回识别文本，用户确认后再调 parse_text
    """
    import asyncio
    from core.asr import asr_sensevoice

    logger.info('[AI] asr_voice 请求')

    try:
        # 读取音频文件内容
        audio_content = await audio_file.read()
        if not audio_content:
            return {'error': '音频文件为空'}

        logger.info(f'[AI] asr_voice 音频大小: {len(audio_content)} bytes')

        # ASR 语音识别（同步函数，用线程池执行）
        transcript = await asyncio.to_thread(asr_sensevoice, None, audio_content)
        if not transcript:
            logger.warning('[AI] asr_voice ASR 识别结果为空')
            return {'error': '语音识别失败，请重试或手动输入'}

        logger.info(f'[AI] asr_voice ASR 识别结果: "{transcript}"')
        return {'data': {'transcript': transcript}}

    except Exception as e:
        logger.error(f'[AI] asr_voice 异常: {e}', exc_info=True)
        return {'error': f'语音识别失败: {str(e)}'}


async def parse_image(image_file, ledger_id: int) -> dict:
    """
    图片解析为交易记录：将图片以 base64 发送给多模态 LLM，直接识别交易信息
    """
    import base64
    from core.llm import unillm

    logger.info(f'[AI] parse_image 请求: ledger_id={ledger_id}')

    try:
        # 读取图片内容
        image_content = await image_file.read()
        if not image_content:
            return {'error': '图片文件为空'}

        # 转 base64
        image_b64 = base64.b64encode(image_content).decode('utf-8')
        # 判断图片类型
        content_type = image_file.content_type or 'image/jpeg'
        logger.info(f'[AI] parse_image 图片大小: {len(image_content)} bytes, type={content_type}')

        today_str = _get_today_str()

        # 构建多模态消息
        messages = [
            {
                'role': 'system',
                'content': IMAGE_PROMPT,
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': f'今天是{today_str}。请识别这张小票/账单图片中的交易信息，提取为JSON。',
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:{content_type};base64,{image_b64}'
                        }
                    }
                ]
            }
        ]

        # 指定使用多模态模型（agnes-2.0-flash）
        raw = await unillm(messages, model_name_list=['agnes-2.0-flash'], temperature=0.1)
        logger.info(f'[AI] parse_image 多模态 LLM 返回: {raw[:500] if raw else "空"}')

        if not raw:
            return {'error': 'AI 服务暂不可用，请稍后重试'}

        # 提取 JSON
        json_str = raw.strip()
        json_match = re.search(r'\{[^}]+\}', json_str, re.DOTALL)
        if json_match:
            json_str = json_match.group()

        result = json.loads(json_str)

        # 校验必要字段
        if 'tx_type' not in result or 'amount' not in result:
            logger.warning(f'[AI] parse_image 缺少必要字段: {result}')
            return {'error': '无法识别图片中的交易信息，请手动输入'}

        # 校验 tx_type
        if result['tx_type'] not in (1, 2):
            return {'error': '无法确定收支类型，请手动输入'}

        # 校验金额
        try:
            result['amount'] = float(result['amount'])
            if result['amount'] <= 0:
                return {'error': '金额必须大于0，请手动输入'}
        except (ValueError, TypeError):
            return {'error': '金额格式错误，请手动输入'}

        # 补全可选字段
        result.setdefault('category', '')
        result.setdefault('remark', '')
        result.setdefault('tx_date', today_str)

        # 校验日期格式
        try:
            datetime.strptime(result['tx_date'], '%Y-%m-%d')
        except ValueError:
            result['tx_date'] = today_str

        logger.info(f'[AI] parse_image 解析成功: {result}')
        return {'data': {'parsed': result}}

    except json.JSONDecodeError:
        logger.warning(f'[AI] parse_image JSON 解析失败, 原始返回: {raw[:200]}')
        return {'error': 'AI 返回格式异常，请手动输入'}
    except Exception as e:
        logger.error(f'[AI] parse_image 异常: {e}', exc_info=True)
        return {'error': f'图片解析失败: {str(e)}'}
