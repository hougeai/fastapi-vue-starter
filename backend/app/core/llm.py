from openai import AsyncOpenAI
from .config import settings
from .log import logger

model_dict = {
    'glm4-flash': {
        'api_key': settings.GLM_KEY,
        'base_url': 'https://open.bigmodel.cn/api/paas/v4',
        'model_name': 'glm-4-flash-250414',
    },
    'qwen2-7b': {
        'api_key': settings.SF_KEY,
        'base_url': 'https://api.siliconflow.cn/v1',
        'model_name': 'Qwen/Qwen2.5-7B-Instruct',
    },
}


class LLM_API:
    def __init__(self, api_key, base_url, model):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def __call__(self, messages, temperature=0.7):
        try:
            completion = await self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature, stream=False
            )
            return completion.choices[-1].message.content
        except Exception as e:
            logger.error(f'LLM error: {e}')
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
            res = await model(messages, temperature=temperature)
            if res:
                return res.strip()
        return ''


unillm = UniLLM()
