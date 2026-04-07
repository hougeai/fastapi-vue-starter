import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import httpx
import asyncio
import json

base_url = 'http://localhost:3002/api/v1/'

client = httpx.Client(base_url=base_url, timeout=60)


def test_user():
    headers = {'token': 'dev'}
    data = {
        'user_name': 'test',
        'password': 'password',
        'email': 'test@test.com',
    }
    response = client.post('user/create', data=json.dumps(data), headers=headers)
    print(response.status_code, response.json())


async def test_oss():
    from core.minio import oss

    # 下载
    all_files = oss.list_objects(prefix='audio/')
    print(all_files)
    for file_key in all_files[:2]:
        print(file_key)
        os.makedirs(os.path.dirname(file_key), exist_ok=True)
        oss.download_file(file_key, file_key)
    # 上传
    objs = os.listdir('./audio')
    for obj in objs:
        audio_key = f'audio/{obj}'
        await oss.upload_file_async(audio_key, file_path=audio_key, content_type='audio/mpeg')
        print(f'{obj} done')
    # 设置public-read
    # oss.set_bucket_public_read()


if __name__ == '__main__':
    test_user()
    asyncio.run(test_oss())
