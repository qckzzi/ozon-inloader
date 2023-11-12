#!/usr/bin/env python
import logging

import requests
from fastapi import (
    FastAPI,
)

import config
from markets_bridge.services import (
    Formatter,
    Sender,
)
from ozon.services import (
    Fetcher,
)


app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


# TODO: Вынести бизнес-логику из ручки и декомпозировать ее
@app.get('/load_ozon_attributes/')
def update_for_category(category_id: int):
    fetcher = Fetcher()

    characteristics = fetcher.get_characteristics(category_id)
    formatted_characteristics = Formatter.format_characteristics(characteristics)
    Sender.send_characteristics(formatted_characteristics)

    characteristic_values = fetcher.get_characteristic_values()
    formatted_characteristic_values = Formatter.format_characteristic_values(characteristic_values)

    existed_characteristic_values = requests.get(config.mb_characteristic_values_url).json()
    existed_value_ids = {value.get('external_id') for value in existed_characteristic_values}
    not_existed_values = list(filter(lambda x: x.external_id not in existed_value_ids, formatted_characteristic_values))

    Sender.send_characteristic_values(not_existed_values)

    if not category_id:
        categories = fetcher.get_categories()
        formatted_categories = Formatter.format_categories(categories)
        Sender.send_categories(formatted_categories)
