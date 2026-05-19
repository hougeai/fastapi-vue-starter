"""
账本、分类、交易 接口测试
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import httpx
import asyncio

base_url = 'http://localhost:3002/api/v1'
client = httpx.Client(base_url=base_url, timeout=60, follow_redirects=True)


def get_headers(token: str = None) -> dict:
    """获取请求头"""
    if token:
        return {'token': token}
    return {}


def test_template(token: str):
    """测试账本模板相关接口"""
    print('\n[账本模板模块]')
    headers = get_headers(token)

    # 1. 获取模板列表
    print('\n1. 获取账本模板列表')
    try:
        response = client.get('ledger/template')
        print(f'状态: {response.status_code}')
        if response.status_code == 200:
            print(f'响应: {response.json()}')
            templates = response.json().get('data', [])
            template_id = templates[0]['id'] if templates else None
        else:
            print(f'响应: {response.json()}')
            template_id = None
    except Exception as e:
        print(f'请求失败: {e}')
        template_id = None

    return template_id


def test_ledger_from_template(token: str, template_id: int):
    """从模板创建账本"""
    print('\n[从模板创建账本]')
    headers = get_headers(token)

    # 从模板创建账本
    print(f'\n1. 从模板(id={template_id})创建账本')
    try:
        response = client.post(
            f'ledger/template/{template_id}/create',
            params={'name': '我的旅行账本', 'description': '去云南玩'},
            headers=headers
        )
        print(f'状态: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'响应: {result}')
            ledger_id = result.get('data', {}).get('ledger', {}).get('id')
            categories = result.get('data', {}).get('categories', [])
            print(f'创建了 {len(categories)} 个预设类别')
        else:
            print(f'响应: {response.json()}')
            ledger_id = None
    except Exception as e:
        print(f'请求失败: {e}')
        ledger_id = None

    return ledger_id


def test_system_categories():
    """测试获取系统预设类别（无需登录）"""
    print('\n[系统预设类别]')
    try:
        response = client.get('ledger/category/system')
        print(f'状态: {response.status_code}')
        try:
            data = response.json()
            print(f'响应: {data}')
            # 统计收入/支出类别数量
            income = [c for c in data.get('data', []) if c.get('tx_type') == 1]
            expense = [c for c in data.get('data', []) if c.get('tx_type') == 2]
            print(f'收入类别: {len(income)}个, 支出类别: {len(expense)}个')
        except Exception:
            print(f'响应文本: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')


def test_ledger(token: str):
    """测试账本相关接口"""
    print('\n[账本模块]')
    headers = get_headers(token)

    # 1. 创建账本
    print('\n1. 创建账本')
    ledger_data = {'name': '我的账本', 'desc': '测试账本'}
    try:
        response = client.post('ledger', json=ledger_data, headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
            ledger_id = response.json().get('data', {}).get('id')
        except Exception:
            print(f'响应文本: {response.text}')
            ledger_id = None
    except Exception as e:
        print(f'请求失败: {e}')
        ledger_id = None

    # 2. 获取账本列表
    print('\n2. 获取账本列表')
    try:
        response = client.get('ledger', headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
        except Exception:
            print(f'响应文本: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

    # 3. 获取账本详情
    if ledger_id:
        print(f'\n3. 获取账本详情 (id={ledger_id})')
        try:
            response = client.get(f'ledger/{ledger_id}', headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')

            # 4. 更新账本
            print(f'\n4. 更新账本 (id={ledger_id})')
            update_data = {'name': '我的账本（已修改）', 'description': '更新后的描述'}
            response = client.put(f'ledger/{ledger_id}', json=update_data, headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')

            # 5. 设为默认账本
            print(f'\n5. 设为默认账本 (id={ledger_id})')
            response = client.post(f'ledger/{ledger_id}/default', headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')
        except Exception as e:
            print(f'请求失败: {e}')

    return ledger_id


def test_category(token: str):
    """测试类别相关接口"""
    print('\n[类别模块]')
    headers = get_headers(token)

    # 1. 获取类别列表
    print('\n1. 获取类别列表')
    try:
        response = client.get('ledger/category', headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
        except Exception:
            print(f'响应文本: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

    # 2. 按类型获取类别（支出）
    print('\n2. 获取支出类别 (type=2)')
    try:
        response = client.get('ledger/category?type=2', headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
        except Exception:
            print(f'响应文本: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

    # 3. 创建类别
    print('\n3. 创建类别')
    category_data = {'name': '餐饮', 'tx_type': 2, 'icon': 'food'}
    try:
        response = client.post('ledger/category', json=category_data, headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
            category_id = response.json().get('data', {}).get('id')
        except Exception:
            print(f'响应文本: {response.text}')
            category_id = None
    except Exception as e:
        print(f'请求失败: {e}')
        category_id = None

    # 4. 更新类别
    if category_id:
        print(f'\n4. 更新类别 (id={category_id})')
        try:
            update_data = {'name': '餐饮（美食）'}
            response = client.put(f'ledger/category/{category_id}', json=update_data, headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')

            # 5. 删除类别
            print(f'\n5. 删除类别 (id={category_id})')
            response = client.delete(f'ledger/category/{category_id}', headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')
        except Exception as e:
            print(f'请求失败: {e}')

    return category_id


def test_transaction(token: str, ledger_id: int):
    """测试交易记录相关接口"""
    print('\n[交易模块]')
    headers = get_headers(token)

    # 1. 获取交易列表
    print(f'\n1. 获取交易列表 (ledger_id={ledger_id})')
    try:
        response = client.get(f'transaction?ledger_id={ledger_id}', headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
        except Exception:
            print(f'响应文本: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

    # 2. 创建交易记录
    print('\n2. 创建交易记录')
    tx_data = {
        'ledger_id': ledger_id,
        'tx_date': '2026-05-19',
        'amount': 100.50,
        'tx_type': 2,
        'category_id': 1,
        'remark': '午餐',
    }
    try:
        response = client.post('transaction', json=tx_data, headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
            tx_id = response.json().get('data', {}).get('id')
        except Exception:
            print(f'响应文本: {response.text}')
            tx_id = None
    except Exception as e:
        print(f'请求失败: {e}')
        tx_id = None

    # 3. 获取收支汇总
    print(f'\n3. 收支汇总 (ledger_id={ledger_id})')
    try:
        response = client.get(f'transaction/summary?ledger_id={ledger_id}', headers=headers)
        print(f'状态: {response.status_code}')
        try:
            print(f'响应: {response.json()}')
        except Exception:
            print(f'响应文本: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

    # 4. 获取交易详情
    if tx_id:
        print(f'\n4. 获取交易详情 (id={tx_id})')
        try:
            response = client.get(f'transaction/{tx_id}', headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')

            # 5. 更新交易
            print(f'\n5. 更新交易 (id={tx_id})')
            update_data = {'remark': '午餐（食堂）', 'amount': 150.00}
            response = client.put(f'transaction/{tx_id}', json=update_data, headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')

            # 6. 删除交易
            print(f'\n6. 删除交易 (id={tx_id})')
            response = client.delete(f'transaction/{tx_id}', headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')
        except Exception as e:
            print(f'请求失败: {e}')

    # 7. 清理：删除账本
    if ledger_id:
        print(f'\n7. 清理账本 (id={ledger_id})')
        try:
            response = client.delete(f'ledger/{ledger_id}', headers=headers)
            print(f'状态: {response.status_code}')
            try:
                print(f'响应: {response.json()}')
            except Exception:
                print(f'响应文本: {response.text}')
        except Exception as e:
            print(f'请求失败: {e}')


async def run_tests(token: str):
    """运行所有测试"""
    print('=' * 60)
    print('账本、分类、交易 接口测试')
    print('=' * 60)

    # 1. 系统预设类别
    # test_system_categories()

    # 2. 账本模板
    template_id = test_template(token)
    if template_id:
        # 3. 从模板创建账本
        ledger_id = test_ledger_from_template(token, template_id)
        if ledger_id:
            # 4. 测试交易（用模板创建的账本）
            test_transaction(token, ledger_id)

    # 5. 普通账本测试
    # ledger_id = test_ledger(token)

    # # 6. 类别模块
    # test_category(token)

    # # 7. 交易模块（用普通账本）
    # if ledger_id:
    #     test_transaction(token, ledger_id)

if __name__ == '__main__':
    token = 'dev'  # 开发模式 token（超级管理员）
    asyncio.run(run_tests(token))
