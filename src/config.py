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
mb_compare_product_characteristics_url = mb_domain + 'api/v1/provider/products/compare_characteristics/'
marketplace_id = int(os.getenv('OZON_ID', default=0))

if not marketplace_id:
    raise ValueError('OZON_ID not set')

mb_login = os.getenv('MB_LOGIN')
mb_password = os.getenv('MB_PASSWORD')

if not (mb_login and mb_password):
    raise ValueError('MB_LOGIN and MB_PASSWORD not set for Markets-Bridge authentication')

mb_token_url = mb_domain + 'api/token/'
mb_token_refresh_url = mb_token_url + 'refresh/'
mb_system_variables_url = mb_domain + 'api/v1/common/system_variables/'
mb_logs_url = mb_domain + 'api/v1/common/logs/'


# OZON
ozon_domain = 'https://api-seller.ozon.ru/'

ozon_categories_url = ozon_domain + 'v1/description-category/tree'
ozon_characteristics_url = ozon_domain + 'v1/description-category/attribute'
ozon_characteristic_values_url = ozon_domain + 'v1/description-category/attribute/values'

# RabbitMQ
mq_user = os.getenv("MQ_USER")
mq_password = os.getenv("MQ_PASSWORD")

if not mq_user or not mq_password:
    raise ValueError("MQ_USER and MQ_PASSWORD not set")

ozon_brand_characteristic_id = 85  # Характеристика "Бренд"
ozon_model_name_characteristic_id = 9048  # Характеристика "Название модели"
ozon_name_characteristic_id = 4180  # Характеристика "Наименование"
ozon_product_type_characteristic_id = 8229  # Характеристика "Тип товара"
ozon_image_characteristic_id = 4194  # Характеристика "Изображение"
