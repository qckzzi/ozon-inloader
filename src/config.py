import os

from dotenv import (
    load_dotenv,
)


load_dotenv()


# Markets-Bridge
mb_domain = os.getenv('MB_DOMAIN')

if not mb_domain:
    raise ValueError('Не задан домен Markets-Bridge.')

mb_categories_url = mb_domain + 'api/v1/recipient/categories/'
mb_relevant_categories_url = mb_categories_url + 'relevant/'
mb_characteristics_url = mb_domain + 'api/v1/recipient/characteristics/'
mb_characteristic_values_url = mb_domain + 'api/v1/recipient/characteristic_values/'
marketplace_id = int(os.getenv('OZON_ID', default=0))

if not marketplace_id:
    raise ValueError('Не задан ID записи маркетплейса "Озон", находящейся в БД Markets-Bridge.')


# OZON
ozon_domain = os.getenv('OZON_DOMAIN')

if not ozon_domain:
    raise ValueError('Не задан домен OZON API.')

ozon_categories_url = ozon_domain + 'v2/category/tree'
ozon_characteristics_url = ozon_domain + 'v3/category/attribute'
ozon_characteristic_values_url = ozon_domain + 'v2/category/attribute/values'

ozon_client_id = os.getenv('OZON_CLIENT_ID')
ozon_api_key = os.getenv('OZON_API_KEY')

if not (ozon_client_id and ozon_api_key):
    raise ValueError('Не заданы Client-Id и Api-Key для доступа к api озона.')
