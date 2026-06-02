import re
import requests
from io import BytesIO
from .config import settings
from .log import logger

def remove_emojis(text):
    emoji_pattern = re.compile("[" u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF" u"\U0001F680-\U0001F6FF" u"\U0001F700-\U0001F77F" u"\U0001F780-\U0001F7FF" u"\U0001F800-\U0001F8FF" u"\U0001F900-\U0001F9FF" u"\U0001FA00-\U0001FA6F" u"\U0001FA70-\U0001FAFF" u"\U00002702-\U000027B0" "+]", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def asr_sensevoice(file_path=None, audio_content=None):
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.SF_KEY}"
    }
    if file_path:
        file_content = open(file_path, "rb")
    elif audio_content:
        file_content = ('file.wav', BytesIO(audio_content))
    else:
        logger.error("No audio file or content provided")
        return ""
    files = {
        "file": file_content,  # The key "file" should match the expected parameter name on the server
        "model": (None, "FunAudioLLM/SenseVoiceSmall")  # "None" is used because model is just a string, not a file
    }
    logger.info(f'[ASR] 请求 SenseVoice 语音识别, model=FunAudioLLM/SenseVoiceSmall')
    response = requests.post(url, files=files, headers=headers)
    if response.status_code == 200:
        data = response.json()
        text = remove_emojis(data["text"])
        logger.info(f'[ASR] 识别成功: "{text}"')
        return text
    else:
        logger.error(f"[ASR] 识别失败: status={response.status_code}, body={response.text[:200]}")
        return ''
   