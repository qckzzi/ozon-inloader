import os

from dotenv import (
    load_dotenv,
)


load_dotenv()


# Markets-Bridge
mb_domain = os.getenv('MB_DOMAIN')

if not mb_domain:
    raise ValueError('MB_DOMAIN not set')

mb_categories_url = mb_domain + 'api/v1/recipient/categories/'
mb_relevant_categories_url = mb_categories_url + 'relevant/'
mb_characteristics_url = mb_domain + 'api/v1/recipient/characteristics/'
mb_characteristic_values_url = mb_domain + 'api/v1/recipient/characteristic_values/'
mb_create_characteristic_matchings_url = mb_domain + 'api/v1/common/characteristic_matchings/create_by_category_matching/'
marketplace_id = int(os.getenv('OZON_ID', default=0))

if not marketplace_id:
    raise ValueError('OZON_ID not set')

mb_login = os.getenv('MB_LOGIN')
mb_password = os.getenv('MB_PASSWORD')

if not (mb_login and mb_password):
    raise ValueError('MB_LOGIN and MB_PASSWORD not set for Markets-Bridge authentication')

mb_token_url = mb_domain + 'api/token/'
mb_token_refresh_url = mb_token_url + 'refresh/'
mb_system_environments_url = mb_domain + 'api/v1/common/system_environments/'
mb_logs_url = mb_domain + 'api/v1/common/logs/'


# OZON
ozon_domain = os.getenv('OZON_API_DOMAIN')

if not ozon_domain:
    raise ValueError('OZON_API_DOMAIN not set')

ozon_categories_url = ozon_domain + 'v2/category/tree'
ozon_characteristics_url = ozon_domain + 'v3/category/attribute'
ozon_characteristic_values_url = ozon_domain + 'v2/category/attribute/values'

ozon_brand_characteristic_id = 85 # Характеристика "Бренд"
ozon_model_name_characteristic_id = 9048 # Характеристика "Название модели"
ozon_name_characteristic_id = 4180 # Характеристика "Наименование"
