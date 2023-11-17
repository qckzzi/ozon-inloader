import logging

import requests

import config
from markets_bridge.types import (
    MBCategory,
    MBCharacteristic,
    MBCharacteristicValue,
)
from ozon.types import (
    OzonCategory,
    OzonCharacteristic,
    OzonCharacteristicValue,
)


class Formatter:
    """Преобразователь данных для сервиса Markets-Bridge."""

    @classmethod
    def format_categories(cls, raw_categories: list[OzonCategory]) -> list[MBCategory]:
        """Форматирует категории озона под шаблон MB категорий.

        Метод также сливает повторяющиеся озон категории из списка raw_categories. У них могут отличаться лишь
        родительские категории. Поэтому если категорию уже отформатировали, то пополняем список родителей.
        """

        result = []

        for category in raw_categories:
            result.append(cls._format_category(category))

        return result

    @classmethod
    def _format_category(cls, category: OzonCategory) -> MBCategory:
        args = (
            category.category_id,
            category.title,
            config.marketplace_id,
            category.parent_id,
        )

        formatted_category = MBCategory(*args)

        return formatted_category

    @classmethod
    def format_characteristics(cls, raw_characteristics: list[OzonCharacteristic]) -> list[MBCharacteristic]:
        """Форматирует характеристики озона под шаблон MB характеристик."""

        formatted_characteristics = []

        for characteristic in raw_characteristics:
            formatted_characteristic = cls._format_characteristic(characteristic)
            formatted_characteristics.append(formatted_characteristic)

        return formatted_characteristics

    @staticmethod
    def _format_characteristic(characteristic: OzonCharacteristic) -> MBCharacteristic:
        formatted_characteristic = MBCharacteristic(
            external_id=characteristic.id,
            name=characteristic.name,
            description=characteristic.description,
            is_required=characteristic.is_required,
            has_reference_values=bool(characteristic.dictionary_id),
            marketplace_id=config.marketplace_id,
            category_external_id=characteristic.category_id,
        )

        return formatted_characteristic

    @classmethod
    def format_characteristic_values(cls, raw_values: list[OzonCharacteristicValue]) -> list[MBCharacteristicValue]:
        """Форматирует значения характеристик озона под шаблон MB значений."""

        result = []

        for value in raw_values:
            result.append(cls._format_characteristic_value(value))

        return result

    @staticmethod
    def _format_characteristic_value(value: OzonCharacteristicValue) -> MBCharacteristicValue:
        formatted_value = MBCharacteristicValue(
            value.id,
            value.value,
            config.marketplace_id,
            value.attribute_id,
        )

        return formatted_value


class Sender:
    """Отправитель данных в сервис Markets-Bridge."""

    @classmethod
    def send_categories(cls, categories: list[MBCategory]):
        cls._send_objects(
            categories,
            url=config.mb_categories_url,
            name='category',
            display_field='name',
        )

    @classmethod
    def send_characteristics(cls, characteristics: list[MBCharacteristic]):
        cls._send_objects(
            characteristics,
            url=config.mb_characteristics_url,
            name='characteristic',
            display_field='name',
        )

    @classmethod
    def send_characteristic_values(cls, values: list[MBCharacteristicValue]):
        cls._send_objects(
            values,
            url=config.mb_characteristic_values_url,
            name='characteristic_value',
            display_field='value',
        )

    @classmethod
    def _send_objects(cls, objects, **kwargs):
        for obj in objects:
            cls._send_object(obj, **kwargs)

    @classmethod
    def _send_object(cls, obj, url, name, display_field):
        headers = get_authorization_headers()
        response = requests.post(url, json=vars(obj), headers=headers)

        if response.status_code == 401:
            accesser = Accesser()
            accesser.update_access_token()
            cls._send_object(obj, url, name, display_field)

            return

        display_value = getattr(obj, display_field)

        if response.status_code == 201:
            logging.info(f'The "{display_value}" {name} has been created.')
        elif response.status_code == 200:
            logging.info(f'The "{display_value}" {name} already exists.')


class Singleton:
    _instance = None
    _initialized = False

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance


class Accesser(Singleton):
    """Получатель доступа к сервису Markets-Bridge.

    При первичном получении токена доступа генерируется JWT. При истечении access токена необходимо вызывать
    update_access_token(). В случае, если refresh токен умер, вызывается метод update_jwt().
    """

    def __init__(self):
        if not self._initialized:
            self._refresh_token = None
            self._access_token = None

            self._initialized = True

    @property
    def access_token(self) -> str:
        if not self._access_token:
            self.update_jwt()

        return self._access_token

    def update_jwt(self):
        login_data = {
            'username': config.mb_login,
            'password': config.mb_password
        }

        response = requests.post(config.mb_token_url, data=login_data)
        response.raise_for_status()
        token_data = response.json()
        self._access_token = token_data['access']
        self._refresh_token = token_data['refresh']

    def update_access_token(self):
        body = {'refresh': self._refresh_token}

        response = requests.post(config.mb_token_refresh_url, json=body)

        if response.status_code == 401:
            self.update_jwt()
            requests.post(config.mb_token_refresh_url, json=body)
            self.update_access_token()

            return

        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data['access']


def write_log_entry(message: str):
    """Создает записи логов в сервисе Markets-Bridge."""

    body = {'service_name': 'OZON attributes inloader', 'entry': message}
    headers = get_authorization_headers()
    response = requests.post(config.mb_logs_url, json=body, headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()
        write_log_entry(message)

        return

    response.raise_for_status()


def get_ozon_client_id() -> str:
    return get_system_environment('OZON_CLIENT_ID')


def get_ozon_api_key() -> str:
    return get_system_environment('OZON_API_KEY')


def get_system_environment(environment_key: str) -> str:
    """Возвращает системную переменную из сервиса Markets-Bridge по ключу."""

    headers = get_authorization_headers()
    response = requests.get(f'{config.mb_system_environments_url}{environment_key}/', headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()

        return get_system_environment(environment_key)

    response.raise_for_status()
    result = response.json()['value']

    return result


def get_existed_characteristic_values() -> dict:
    headers = get_authorization_headers()
    response = requests.get(config.mb_characteristic_values_url, headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()

        return get_existed_characteristic_values()

    response.raise_for_status()

    return response.json()


def get_existed_categories() -> dict:
    headers = get_authorization_headers()
    response = requests.get(config.mb_categories_url, headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()

        return get_existed_categories()

    response.raise_for_status()

    return response.json()


def create_characteristic_matchings(category_matching_id: int):
    body = {'category_matching_id': category_matching_id}
    headers = get_authorization_headers()
    response = requests.post(config.mb_create_characteristic_matchings_url, json=body, headers=headers)

    if response.status_code == 401:
        accesser = Accesser()
        accesser.update_access_token()
        create_characteristic_matchings(category_matching_id)

        return

    response.raise_for_status()


def get_authorization_headers() -> dict:
    accesser = Accesser()
    access_token = accesser.access_token
    headers = {'Authorization': f'Bearer {access_token}'}

    return headers
