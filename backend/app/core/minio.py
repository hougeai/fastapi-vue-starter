import os
import json
import base64
import asyncio
import soundfile as sf
import scipy.signal as signal
import numpy as np
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject
from pydub import AudioSegment

from .config import settings
from .log import logger

# 获取环境变量中的MinIO配置
minio_endpoint = settings.OSS_ENDPOINT
minio_access_key = settings.OSS_ACCESS_KEY_ID
minio_secret_key = settings.OSS_ACCESS_KEY_SECRET
minio_bucket_name = settings.OSS_BUCKET_NAME
minio_region = settings.OSS_REGION
minio_secure = settings.OSS_SECURE


class MinIO:
    def __init__(self):
        endpoint = (minio_endpoint or '').strip()
        if not endpoint:
            raise ValueError('MinIO endpoint is not configured')
        self.client = Minio(
            endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_secure,  # 是否启用HTTPS，需要根据部署的minio进行选择
            region=minio_region,
        )
        self.bucket_name = minio_bucket_name
        self.valid_rates = [8000, 12000, 16000, 24000, 48000]
        self.target_rate = 16000

        # 确保存储桶存在
        found = self.client.bucket_exists(self.bucket_name)
        if not found:
            self.client.make_bucket(self.bucket_name)

    def set_bucket_public_read(self):
        """设置bucket为public-read权限"""
        policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': '*',
                    'Action': ['s3:GetObject'],
                    'Resource': [f'arn:aws:s3:::{self.bucket_name}/*'],
                }
            ],
        }
        try:
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            return True
        except S3Error as e:
            logger.error(f'Error setting bucket policy: {e}')
            return False

    def upload_audio(self, key, audio_path=None, audio_data=None, audio_text=''):
        if audio_path:
            data, samplerate = sf.read(audio_path)
        elif audio_data:
            # 尝试用 pydub 读取任意格式（支持 webm/ogg/opus）
            audio = AudioSegment.from_file(BytesIO(audio_data))
            samplerate = audio.frame_rate
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            data = samples / np.iinfo(audio.array_type).max
        if samplerate not in self.valid_rates:
            num_samples = round(len(data) * self.target_rate / samplerate)
            data = signal.resample(data, num_samples)
            samplerate = self.target_rate
        with BytesIO() as f:
            sf.write(f, data, samplerate, format='ogg', subtype='OPUS')
            f.seek(0)
            text64 = base64.b64encode(audio_text.encode())
            try:
                self.client.put_object(
                    self.bucket_name,
                    key,
                    f,
                    length=f.getbuffer().nbytes,
                    metadata={'text': text64.decode()},
                    content_type='audio/ogg',
                )
                return True
            except S3Error as e:
                logger.error(f'Error uploading audio: {e}')
                return False

    def download_audio(self, key, save_path):
        try:
            response = self.client.get_object(self.bucket_name, key)
            # 读取元数据
            meta_data = response.headers.get('X-Amz-Meta-Text')
            text = base64.b64decode(meta_data).decode() if meta_data else ''

            with BytesIO(response.data) as audio_data:
                temp_ogg = BytesIO()
                temp_ogg.write(audio_data.read())
                temp_ogg.seek(0)
                data, samplerate = sf.read(temp_ogg)
                sf.write(save_path, data, samplerate, format='wav')
            return text
        except S3Error as e:
            if e.code == 'NoSuchKey':
                logger.error(f'Object {key} does not exist in the bucket.')
            else:
                logger.error(f'Error downloading object: {e}')
            return None
        except Exception as e:
            logger.error(f'Error downloading object: {e}')
            return None
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

    def download_file(self, key, save_path):
        try:
            response = self.client.get_object(self.bucket_name, key)
            with open(save_path, 'wb') as f:
                for data in response.stream(32 * 1024):  # 32KB chunks
                    f.write(data)
                return True
        except S3Error as e:
            logger.error(f'Error downloading file: {e}')
            return False
        except Exception as e:
            logger.error(f'Error downloading file: {e}')
            return False
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

    def delete_file(self, key):
        try:
            self.client.remove_object(self.bucket_name, key)
            return True
        except S3Error as e:
            logger.error(f'Error deleting object: {e}')
            return False

    def delete_batch(self, keys):
        try:
            # MinIO支持批量删除，但需要分批处理，每批最多1000个
            for i in range(0, len(keys), 1000):
                batch = [DeleteObject(key) for key in keys[i : i + 1000]]
                errors = self.client.remove_objects(self.bucket_name, batch)
                for error in errors:
                    logger.error(f'Error deleting object {error.object_name}: {error.message}')
            return True
        except S3Error as e:
            logger.error(f'Error deleting batch: {e}')
            return False

    def check_key_exists(self, key):
        try:
            self.client.stat_object(self.bucket_name, key)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            else:
                logger.error(f'Error checking object existence: {e}')
                return False

    def upload_file(self, key, file_path=None, file_data=None, content_type='application/octet-stream'):
        if file_path:
            stat = os.stat(file_path)
            with open(file_path, 'rb') as f:
                try:
                    self.client.put_object(self.bucket_name, key, f, stat.st_size, content_type)
                    return True
                except S3Error as e:
                    logger.error(f'Error uploading file {key}: {e}')
                    return False
        elif file_data:
            with BytesIO(file_data) as f:
                try:
                    self.client.put_object(self.bucket_name, key, f, len(file_data), content_type)
                    return True
                except S3Error as e:
                    logger.error(f'Error uploading file data {key}: {e}')
                    return False
        return False

    def list_objects(self, prefix=None):
        keys = []
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)
            for obj in objects:
                if obj.object_name.endswith('/'):
                    continue
                keys.append(obj.object_name)
            return keys
        except S3Error as e:
            logger.error(f'Error listing objects: {e}')
            return keys

    async def upload_file_async(self, key, file_path=None, file_data=None, content_type='application/octet-stream'):
        """异步上传文件"""
        return await asyncio.to_thread(self.upload_file, key, file_path, file_data, content_type)

    async def upload_audio_async(self, key, audio_path=None, audio_data=None, audio_text=''):
        """异步上传音频"""
        return await asyncio.to_thread(self.upload_audio, key, audio_path, audio_data, audio_text)

    async def delete_file_async(self, key):
        """异步删除文件"""
        return await asyncio.to_thread(self.delete_file, key)


# 创建对象存储示例
oss = None
try:
    oss = MinIO()
except Exception as e:
    logger.warning('MinIO not initialized: %s', e)
