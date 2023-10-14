#!/usr/bin/env python
"""Основной модуль запуска загрузчика."""
import requests

from core import (
    config,
    secret_config,
)


def main():
    """Docstring."""
    client_id = secret_config.get('ozon', 'client_id')
    api_key = secret_config.get('ozon', 'api_key')
    headers = {'Client-Id': client_id, 'Api-Key': api_key}

    categories_url = config.get('ozon', 'categories_url')

    response_data = requests.post(categories_url, headers=headers).json()

    categories = response_data.get('result')

    categories_url = config.get('markets_bridge', 'recipient_categories_url')
    
    existed_categories = requests.get(categories_url).json()
    existed_external_ids = set(record.get('external_id') for record in existed_categories)
    unpacked_categories, unpacked_product_types = unpack_categories(categories, existed_external_ids)

    # send_categories(unpacked_categories)
    # send_product_types(unpacked_product_types)

    # parse_attributes()
    # category_attributes_url = config.get('ozon', 'category_attributes_url')
    # category_attributes_json = requests.post(category_attributes_url, json=dict(category_id=115946522), headers=headers).json()
    # category_attributes = category_attributes_json.get('categoryAttributes')
    # processed_attributes, processed_attribute_values = unpack_attributes(category_attributes)
    # send_attributes(processed_attributes)
    # send_attribute_values(processed_attribute_values)


def unpack_categories(categories, existed_ids, parent_id=None):
    unpacked_categories = []
    unpacked_product_types = []

    recipient_marketplace_id = config.get('markets_bridge', 'marketplace_id')

    for category_data in categories:

        if product_type_id := category_data.get('type_id'):
            unpacked_product_types.append(
                dict(
                    external_id=product_type_id,
                    name=category_data.get('type_name'),
                    category=parent_id,
                )
            )

        if not category_data['disabled'] and not product_type_id:
            if category_data.get('category_id') not in existed_ids:
                category = dict(
                    external_id=category_data.get('category_id'),
                    name=category_data.get('category_name'),
                    recipient_marketplace=recipient_marketplace_id,
                    parent=parent_id,
                )
                send_category(category)
                unpacked_categories.append(category)

        if category_data['children']:
            sub_categories, product_types = unpack_categories(
                category_data['children'],
                existed_ids,
                parent_id=category_data.get('category_id'),
            )
            unpacked_categories.extend(sub_categories)
            unpacked_product_types.extend(product_types)

    return unpacked_categories, unpacked_product_types


def send_category(category):
    # new_categories = list(
    #     filter(
    #         lambda category: category.get('external_id')
    #         not in existed_external_ids, categories
    #     )
    # )

    # new_categories = sorted(new_categories, key=lambda x: x['external_id'])
    
    # for new_category in new_categories:

    categories_url = config.get('markets_bridge', 'recipient_categories_url')

    # existed_categories = requests.get(categories_url).json()
    # existed_external_ids = set(record.get('external_id') for record in existed_categories)


    post_response = requests.post(categories_url, json=category)

    if post_response.status_code == 201:
        category = post_response.json()
        cat_id = category.get('id')
        name = category.get('name')
        post_message = f'Created: id = {cat_id}, name = {name}'
    else:
        post_message = (
            'Unexpected response from the server:\nCategory: '
            f'{category.get('name')} ({post_response.status_code})\n'
        )

    print(post_message)


def send_product_types(product_types):
    print('Creating product types...')
    product_types_url_url = config.get('markets_bridge', 'recipient_product_types_url')

    existed_product_types = requests.get(product_types_url_url).json()

    existed_external_ids = set(record.get('external_id') for record in existed_product_types)

    new_product_types = list(
        filter(
            lambda type: type.get('external_id')
            not in existed_external_ids, product_types
        )
    )
    
    post_response = requests.post(product_types_url_url, json=new_product_types)

    if post_response.status_code == 201:
        post_message = f'Created: {len(post_response.json())}\n'
    else:
        post_message = f'Unexpected response from the server:\n{post_response.status_code}\n'

    print(post_message)


def parse_attributes():
    """..."""


if __name__ == '__main__':
    main()
