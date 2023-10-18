import requests

from configs import (
    config,
    secret_config,
)


def process_categories():
    ozon_categories_url = config.get('ozon', 'categories_url')

    client_id = secret_config.get('ozon', 'client_id')
    api_key = secret_config.get('ozon', 'api_key')
    headers = {'Client-Id': client_id, 'Api-Key': api_key}

    ozon_response = requests.post(ozon_categories_url, headers=headers)
    
    if ozon_response.status_code != 200:
        print(f'Unexpected response from the server.\nCODE: {ozon_response.status_code}\n')

        return

    ozon_categories = ozon_response.json().get('result')

    unpacked_categories = unpack_categories(ozon_categories)


def send_categories(ozon_categories, parent_id=None):
    for ozon_category in ozon_categories:
        category = dict(
            external_id=ozon_category.get('category_id') or ozon_category.get('type_id'),
            name=ozon_category.get('category_name') or ozon_category.get('type_name'),
            recipient_marketplace=config.get('markets_bridge', 'marketplace_id'),
            parent_categories=parent_id,
        )
        send_category(category)

        if ozon_category['children']:
            children = ozon_category.get('children')
            parent_id = ozon_category.get('category_id')
            send_categories(children, parent_id)


def send_category(category):
    mb_categories_url = config.get('markets_bridge', 'recipient_categories_url')
    mb_response = requests.post(mb_categories_url, json=category)

    if mb_response.status_code == 201:
        created_category = mb_response.json()
        created_category_id = created_category.get('id')
        created_category_name = created_category.get('name')
        post_message = f'Created: id = {created_category_id}, name = {created_category_name}'
    else:
        post_message = (
            'Unexpected response from the server:\nCategory: '
            f'{category.get('name')} (CODE: {mb_response.status_code})\n'
        )

    print(post_message)


def unpack_categories(ozon_categories: list, parent_id: int = None):
    for ozon_category in ozon_categories:
        category = dict(
            external_id=ozon_category.get('category_id') or ozon_category.get('type_id'),
            name=ozon_category.get('category_name') or ozon_category.get('type_name'),
            recipient_marketplace=config.get('markets_bridge', 'marketplace_id'),
            parent_categories=parent_id,
        )
        send_category(category)

        if ozon_category['children']:
            children = ozon_category.get('children')
            parent_id = ozon_category.get('category_id')
            send_categories(children, parent_id)


def unpack_categories(ozon_categories: list, parents: list = None):
    result = []
    if parents is None:
        parents = []

    for category in ozon_categories:
        name = category.get('name')
        external_id = category.get('category_id') or category.get('type_id'),
        name = category.get('category_name') or category.get('type_name'),
        recipient_marketplace = config.get('markets_bridge', 'marketplace_id'),
        parent_categories = parent_id,
        current_parents = parents + [name]

        # Добавляем текущий элемент
        result.append({'name': name, 'parents': current_parents})

        # Рекурсивно обрабатываем вложенные элементы, если они есть
        if 'children' in item:
            result.extend(flatten_tree(item['children'], current_parents))

    return result
