#!/usr/bin/env python
"""Основной модуль запуска загрузчика."""
from category_processing import (
    process_categories,
)
from characteristic_processing import (
    process_characteristics,
)


def main():
    process_categories()
    process_characteristics()


if __name__ == '__main__':
    main()
