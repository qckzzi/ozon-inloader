#!/usr/bin/env python
"""Основной модуль запуска загрузчика."""
from category_processing import (
    process_categories,
)
from characteristic_processing import (
    process_characteristics,
)
from config import (
    config,
    secret_config,
)


def main():
    client_id = secret_config.get('ozon', 'client_id')
    api_key = secret_config.get('ozon', 'api_key')
    headers = {'Client-Id': client_id, 'Api-Key': api_key}

    ozon_categories_url = config.get('ozon', 'categories_url')
    mb_categories_url = config.get('markets_bridge', 'recipient_categories_url')
    marketplace_id = config.get('markets_bridge', 'marketplace_id')
    process_categories(
        headers,
        ozon_categories_url,
        mb_categories_url,
        marketplace_id,
    )

    ozon_characteristics_url = config.get('ozon', 'category_attributes_url')
    mb_characteristics_url = config.get('markets_bridge', 'recipient_characteristics_url')
    related_types_url = config.get('markets_bridge', 'related_types_url')

    process_characteristics(
        headers,
        ozon_characteristics_url,
        mb_characteristics_url,
        related_types_url,
    )


if __name__ == '__main__':
    main()
