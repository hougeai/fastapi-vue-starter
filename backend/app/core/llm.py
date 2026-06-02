import asyncio
from openai import AsyncOpenAI
from .config import settings
from .log import logger

model_dict = {
    'deepseek-ai/DeepSeek-V4-Flash': {
        'api_key': settings.SF_KEY,
        'base_url': 'https://api.siliconflow.cn/v1',
        'model_name': 'deepseek-ai/DeepSeek-V4-Flash',
    },
    'qwen3.5-4b': {
        'api_key': settings.SF_KEY,
        'base_url': 'https://api.siliconflow.cn/v1',
        'model_name': 'Qwen/Qwen3.5-4B',
    },
    'glm-4.7-flash': {
        'api_key': settings.GLM_KEY,
        'base_url': 'https://open.bigmodel.cn/api/paas/v4',
        'model_name': 'glm-4.7-flash',
    },
    
}


class LLM_API:
    def __init__(self, api_key, base_url, model):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def __call__(self, messages, temperature=0.7, timeout=45):
        try:
            completion = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=temperature, stream=False
                ),
                timeout=timeout
            )
            return completion.choices[-1].message.content
        except asyncio.TimeoutError:
            logger.error(f'LLM timeout: 模型 {self.model} 超过 {timeout}s 未响应')
            return ''
        except Exception as e:
            logger.error(f'LLM error: 模型 {self.model}, {e}')
            return ''


class UniLLM:
    def __init__(self):
        model_names = list(model_dict.keys())
        self.models = {
            name: LLM_API(
                api_key=model_dict[name]['api_key'],
                base_url=model_dict[name]['base_url'],
                model=model_dict[name]['model_name'],
            )
            for name in model_names
        }

    async def __call__(self, messages, model_name_list=list(model_dict.keys()), temperature=0.7):
        for model_name in model_name_list:
            model = self.models.get(model_name)
            logger.info(f'[LLM] 调用模型: {model_name} ({model.model}), temperature={temperature}')
            res = await model(messages, temperature=temperature)
            if res:
                logger.info(f'[LLM] 模型 {model_name} 返回成功, 长度={len(res)}')
                return res.strip()
            else:
                logger.warning(f'[LLM] 模型 {model_name} 返回为空，尝试下一个')
        return ''


unillm = UniLLM()
