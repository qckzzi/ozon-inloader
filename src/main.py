#!/usr/bin/env python
"""Основной модуль запуска загрузчика."""
import argparse

import requests

import config
from markets_bridge.services import (
    Formatter,
    Sender,
)
from ozon.services import (
    Fetcher,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--category_id',
        type=int,
        default=0,
        help='Идентификатор категории, для которой загрузятся характеристики',
    )
    args = parser.parse_args()

    fetcher = Fetcher()

    characteristics = fetcher.get_characteristics(args.category_id)
    formatted_characteristics = Formatter.format_characteristics(characteristics)
    Sender.send_characteristics(formatted_characteristics)

    characteristic_values = fetcher.get_characteristic_values()
    formatted_characteristic_values = Formatter.format_characteristic_values(characteristic_values)
    existed_characteristic_values = requests.get(config.mb_characteristic_values_url).json()
    existed_value_ids = {value.get('external_id') for value in existed_characteristic_values}
    not_existed_values = list(filter(lambda x: x.external_id not in existed_value_ids, formatted_characteristic_values))
    Sender.send_characteristic_values(not_existed_values)

    if not args.category_id:
        categories = fetcher.get_categories()
        formatted_categories = Formatter.format_categories(categories)
        Sender.send_categories(formatted_categories)


if __name__ == '__main__':
    main()
