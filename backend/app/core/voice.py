import re
import wave
import aiohttp
from io import BytesIO
from .config import settings
from .log import logger

aud_text = {
    '中文': '欢迎使用AI全能播让AI声音成为你直播的新引擎。在这里，你只需一段语音，即可快速克隆你的专属音色，生成高品质音频内容，轻松用于各种直播场景。无需复杂操作，无需反复录制，把声音的事交给我们。',
    '英语': 'You can easily clone your own unique voice and generate high-quality audio content for various live scenarios. Simply record a short audio clip, and we will process it to create a personalized voice for you. ',
}


def remove_emojis(text):
    emoji_pattern = re.compile(
        '['
        '\U0001f600-\U0001f64f'
        '\U0001f300-\U0001f5ff'
        '\U0001f680-\U0001f6ff'
        '\U0001f700-\U0001f77f'
        '\U0001f780-\U0001f7ff'
        '\U0001f800-\U0001f8ff'
        '\U0001f900-\U0001f9ff'
        '\U0001fa00-\U0001fa6f'
        '\U0001fa70-\U0001faff'
        '\U00002702-\U000027b0'
        '+]',
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)


def pcm2wav(pcm_data, frame_rate=24000):
    with BytesIO() as buffer:
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)  # 设置声道数
            wav.setsampwidth(2)  # 设置采样宽度 (16-bit)
            wav.setframerate(frame_rate)  # 设置采样率
            wav.writeframes(pcm_data)  # 写入 PCM 数据
        wav_data = buffer.getvalue()
        return wav_data


async def asr_sensevoice(file_path=None, audio_content=None):
    url = 'https://api.siliconflow.cn/v1/audio/transcriptions'
    headers = {'accept': 'application/json', 'Authorization': f'Bearer {settings.SF_KEY}'}

    if file_path:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        data = aiohttp.FormData()
        data.add_field('file', file_content, filename='file.wav')
        data.add_field('model', 'FunAudioLLM/SenseVoiceSmall')
    elif audio_content:
        data = aiohttp.FormData()
        data.add_field('file', BytesIO(audio_content), filename='file.wav')
        data.add_field('model', 'FunAudioLLM/SenseVoiceSmall')
    else:
        logger.error('No audio file or content provided')
        return ''

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return remove_emojis(result['text'])
                else:
                    logger.error(f'Failed to get ASR result from SenseVoice: {response.status}')
                    return ''
    except Exception as e:
        logger.error(f'Failed to get ASR result from SenseVoice, error: {e}')
        return ''


class IndexTtsService:
    def __init__(self):
        self.url = settings.INDEXTTS_URL

    async def register_speaker(self, voice_id: str):
        try:
            url = f'{self.url}/register-speaker-minio'
            data = {'voice_id': voice_id}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f'Failed to register speaker from minio: {response.status}')
                        return {'status': 'failed', 'message': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f'Failed to register speaker from minio, error: {e}')
            return {'status': 'failed', 'message': str(e)}

    async def infer(self, voice_id: str, tts_text: str):
        try:
            # 构造请求URL
            url = f'{self.url}/infer-minio'
            data = {'voice_id': voice_id, 'tts_text': tts_text}
            # 发送异步POST请求
            pcm = b''
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(16000):
                            pcm += chunk
                        return pcm
                    else:
                        logger.error(f'Failed to synthesize speech from minio: {response.status}')
                        return None
        except Exception as e:
            logger.error(f'Failed to synthesize speech from minio, error: {e}')
            return None


indextts_service = IndexTtsService()
