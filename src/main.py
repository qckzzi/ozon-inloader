#!/usr/bin/env python
"""Основной модуль запуска загрузчика."""
from markets_bridge.services import (
    Formatter,
    Sender,
)
from ozon.services import (
    Fetcher,
)


def main():
    fetcher = Fetcher()

    characteristics = fetcher.get_characteristics()
    formatted_characteristics = Formatter.format_characteristics(characteristics)
    Sender.send_characteristics(formatted_characteristics)

    characteristic_values = fetcher.get_characteristic_values()
    formatted_characteristic_values = Formatter.format_characteristic_values(characteristic_values)
    Sender.send_characteristic_values(formatted_characteristic_values)

    categories = fetcher.get_categories()
    formatted_categories = Formatter.format_categories(categories)
    Sender.send_categories(formatted_categories)


if __name__ == '__main__':
    main()
