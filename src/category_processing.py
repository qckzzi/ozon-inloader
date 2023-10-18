import requests


def process_categories(
        headers: dict,
        categories_url: str,
        existed_categories_url: str,
        recipient_marketplace_id: int,
        product_types_url: str,
):
    categories_response = requests.post(categories_url, headers=headers)
    
    if categories_response.status_code != 200:
        print(f'Unexpected response from the server:\n{categories_response.status_code}\n')

    categories = categories_response.json().get('result')
    existed_categories_response = requests.get(existed_categories_url)

    if existed_categories_response.status_code != 200:
        print(f'Unexpected response from the server:\n{existed_categories_response.status_code}\n')


    existed_category_external_ids = set(
        category.get('external_id') for category in existed_categories_response.json()
    )

    unpacked_product_types = unpack_categories(
        categories,
        existed_category_external_ids,
        recipient_marketplace_id,
        existed_categories_url,
    )

    send_product_types(unpacked_product_types.values(), product_types_url)


# TODO: Пофиксить присвоение нескольких категорий одному типу товара, разделить логику создания категории и создания типа товара
def unpack_categories(
        categories,
        existed_ids,
        marketplace_id,
        existed_categories_url,
        parent_id=None,
) -> dict:
    unpacked_product_types = {}

    for category_data in categories:

        if product_type_id := category_data.get('type_id'):
            if product_type_id in unpacked_product_types:
                unpacked_product_types[product_type_id]['category'].append(parent_id)
            else:
                unpacked_product_types[product_type_id] = dict(
                        external_id=product_type_id,
                        name=category_data.get('type_name'),
                        category=[parent_id],
                )

        else:
            if category_data.get('category_id') not in existed_ids:
                category = dict(
                    external_id=category_data.get('category_id'),
                    name=category_data.get('category_name'),
                    recipient_marketplace=marketplace_id,
                    parent=parent_id,
                )
                send_category(category, existed_categories_url)

        if category_data['children']:
            product_types = unpack_categories(
                category_data['children'],
                existed_ids,
                marketplace_id,
                existed_categories_url,
                parent_id=category_data.get('category_id'),
            )
            unpacked_product_types.update(product_types)

    return unpacked_product_types


def send_category(category, existed_categories_url):
    post_response = requests.post(existed_categories_url, json=category)

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


def send_product_types(product_types, product_types_url):
    print('Creating product types...')

    existed_product_types = requests.get(product_types_url).json()

    existed_external_ids = set(record.get('external_id') for record in existed_product_types)

    new_product_types = list(
        filter(
            lambda type: type.get('external_id') not in existed_external_ids, 
            product_types
        )
    )
    
    post_response = requests.post(product_types_url, json=new_product_types)

    if post_response.status_code == 201:
        post_message = f'Created: {len(post_response.json())}\n'
    else:
        post_message = f'Unexpected response from the server:\n{post_response.status_code}\n'

    print(post_message)