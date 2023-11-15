#!/usr/bin/env python
import json
import logging

import pika
import requests

import config
from markets_bridge.utils import (
    Formatter,
    Sender,
    get_existed_characteristic_values,
    write_log_entry,
)
from ozon.utils import (
    Fetcher,
)


def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        operation_type = message['method']

        logging.info(f'Message was received. Operation is "{operation_type.lower()}"')

        match operation_type:
            case 'LOAD_FOR_CATEGORY':
                load_ozon_attributes_for_category(message['category_external_id'], message['matching_id'])
            case 'LOAD_CATEGORIES':
                load_categories()

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

def load_ozon_attributes_for_category(category_id: int, matching_id: int):
    fetcher = Fetcher()

    characteristics = fetcher.get_characteristics(category_id)
    formatted_characteristics = Formatter.format_characteristics(characteristics)
    Sender.send_characteristics(formatted_characteristics)

    characteristic_values = fetcher.get_characteristic_values()
    formatted_characteristic_values = Formatter.format_characteristic_values(characteristic_values)

    existed_characteristic_values = get_existed_characteristic_values()
    existed_value_ids = {value.get('external_id') for value in existed_characteristic_values}
    not_existed_values = list(filter(lambda x: x.external_id not in existed_value_ids, formatted_characteristic_values))

    Sender.send_characteristic_values(not_existed_values)
    body = {'category_matching_id': matching_id}
    requests.post(config.mb_create_characteristic_matchings_url, json=body)

def load_categories():
    fetcher = Fetcher()

    categories = fetcher.get_categories()
    formatted_categories = Formatter.format_categories(categories)

    existed_categories = requests.get(config.mb_categories_url).json()
    existed_value_ids = {category.get('external_id') for category in existed_categories}
    not_existed_categories = list(filter(lambda x: x.external_id not in existed_value_ids, formatted_categories))

    Sender.send_categories(not_existed_categories)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    connection_parameters = pika.ConnectionParameters(host='localhost', heartbeat=300, blocked_connection_timeout=300)
    with pika.BlockingConnection(connection_parameters) as connection:
        channel = connection.channel()
        channel.queue_declare('inloading')
        channel.basic_consume('inloading', callback, auto_ack=True)
        channel.start_consuming()