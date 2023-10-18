import requests


def process_characteristics(
    headers: dict,
    ozon_characteristics_url: str,
    mb_characteristics_url: str,
    related_types_url: str,
):

    mb_char_response = requests.get(mb_characteristics_url)
    mb_char_response_json = mb_char_response.json()

    related_types_response = requests.get(related_types_url)
    related_types_response_json = related_types_response.json()

    char_list = []

    for related_type in related_types_response_json:
        ozon_response = requests.post(
            ozon_characteristics_url,
            json={
                'category_id': related_type.get('category_external_id'), 
                'type_id': related_type.get('external_id'), 
            },
            headers=headers,
        )
        ozon_response_json = ozon_response.json()

        if ozon_response.status_code != 200:
            print(f'Ошика получения атрибутов OZON:\n{ozon_response_json.get('message')}')

            continue

        formated_chars = format_chars(
            ozon_response_json.get('result'),
            related_type.get('category_external_id'),
            related_type.get('external_id'),
        )

        char_list.extend(formated_chars)

    chars = merge_chars(char_list)
    response = requests.post(mb_characteristics_url, json=chars)

    if response.status_code == 201:
        print('Всё заебись')
    else:
        print('Всё не заебись')


def format_chars(chars, type_id, category_id) -> list:
    result = []

    for char in chars:
        result.append(
            dict(
                name=char.get('name'),
                external_id=char.get('id'),
                recipient_product_type=[type_id],
                recipient_category=[category_id],
            )
        )

    return result


def merge_chars(chars):
    found_chars = {}

    for char in chars:
        if (external_id := char.get('external_id')) not in found_chars:
            found_chars[external_id] = char
        else:
            found_chars[external_id]['recipient_product_type'].extend(
                char['recipient_category'],
            )

            found_chars[external_id]['recipient_category'].extend(
                char['recipient_category']
            )

    return list(found_chars.values())

