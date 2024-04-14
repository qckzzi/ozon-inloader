#!/usr/bin/env python
import json
import logging

import pika

from markets_bridge.utils import (
    Formatter,
    Sender,
    compare_product_characteristics,
    create_characteristic_matchings,
    get_existed_categories,
    get_existed_characteristic_values,
    get_existed_characteristics,
    write_log_entry,
)
from ozon.utils import (
    Fetcher,
)
import config


def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        operation_type = message['method']

        logging.info(f'Message was received. Operation is "{operation_type.lower()}"')

        match operation_type:
            case 'LOAD_FOR_CATEGORY':
                load_ozon_attributes_for_category(
                    message['category_external_id'],
                    message['product_type_external_id'],
                    message['matching_id']
                )
            case 'LOAD_FOR_PRODUCT':
                load_ozon_attributes_for_product(
                    message['category_external_id'],
                    message['product_type_external_id'],
                    message['product_id']
                )
            case 'LOAD_CATEGORIES':
                load_categories()
            case 'LOAD_BRANDS':
                load_brands(categories=message['categories'])

    except KeyError as e:
        error = f'Body validation error: {e}'
        write_log_entry(error)
        logging.error(error)
        return
    except Exception as e:
        error = f'There was a problem: {e}'
        write_log_entry(error)
        logging.exception(error)
        return


def load_ozon_attributes_for_product(category_id: int, product_type_external_id: int, product_id: int):
    load_ozon_attributes(category_id, product_type_external_id)
    compare_product_characteristics(product_id)


def load_ozon_attributes_for_category(category_id: int, product_type_external_id: int, matching_id: int):
    load_ozon_attributes(category_id, product_type_external_id)
    create_characteristic_matchings(matching_id)


def load_ozon_attributes(category_id: int, product_type_external_id: int):
    fetcher = Fetcher()

    characteristics = fetcher.get_characteristics(category_id, product_type_external_id)
    formatted_characteristics = Formatter.format_characteristics(characteristics)
    existed_chars = get_existed_characteristics()
    existed_char_ids = {ch.get('external_id') for ch in existed_chars}
    not_existed_chars = list(filter(lambda x: x.external_id not in existed_char_ids, formatted_characteristics))

    if not_existed_chars:
        Sender.send_characteristics(formatted_characteristics)

    characteristic_values = fetcher.get_characteristic_values()
    formatted_characteristic_values = Formatter.format_characteristic_values(characteristic_values)

    existed_characteristic_values = get_existed_characteristic_values()
    existed_value_ids = {value.get('external_id') for value in existed_characteristic_values}
    not_existed_values = list(filter(lambda x: x.external_id not in existed_value_ids, formatted_characteristic_values))

    if not_existed_values:
        Sender.send_characteristic_values(not_existed_values)
    

def load_categories():
    fetcher = Fetcher()

    categories = fetcher.get_categories()
    formatted_categories = Formatter.format_categories(categories)

    existed_categories = get_existed_categories()
    existed_category_ids = {category.get('external_id') for category in existed_categories}

    not_existed_categories = list(filter(lambda x: x.external_id not in existed_category_ids, formatted_categories))

    Sender.send_categories(not_existed_categories)


def load_brands(categories: list[dict]):
    for category in categories:
        try:
            fetcher = Fetcher()

            brand_values = fetcher.get_brand_values(category['product_type_external_id'], category['category_external_id'])
            formatted_brand_values = Formatter.format_characteristic_values(brand_values)

            existed_characteristic_values = get_existed_characteristic_values()
            existed_value_ids = {value.get('external_id') for value in existed_characteristic_values}

            not_existed_brands = list(filter(lambda x: x.external_id not in existed_value_ids, formatted_brand_values))
            Sender.send_characteristic_values(not_existed_brands)
        except Exception as e:
            error = f'There was a problem: {e}'
            write_log_entry(error)
            logging.exception(error)
            continue


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    credo = pika.PlainCredentials(username=config.mq_user, password=config.mq_password)
    connection_parameters = pika.ConnectionParameters(
        host='localhost',
        heartbeat=300,
        blocked_connection_timeout=300,
        credentials=credo,
    )
    with pika.BlockingConnection(connection_parameters) as connection:
        channel = connection.channel()
        channel.queue_declare('inloading', durable=True)
        channel.basic_consume('inloading', callback, auto_ack=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            pass
