import requests

import config
from markets_bridge.utils import (
    get_ozon_api_key,
    get_ozon_client_id,
)
from ozon.types import (
    OzonCategory,
    OzonCharacteristic,
    OzonCharacteristicValue,
)


# FIXME: DRY и KISS
class Fetcher:
    """Сборщик данных OZON.

    Собирает и хранит в себе атрибуты внешней системы. Возвращает их в таком виде, в каком и получил.
    """

    def __init__(self):
        self._categories: list[OzonCategory] = []
        self._characteristics: list[OzonCharacteristic] = []
        self._characteristic_values: list[OzonCharacteristicValue] = []

        self._headers = None

    def get_categories(self) -> list[OzonCategory]:
        return self._get_categories_from_ozon()

    def get_characteristics(self, external_category_id: int = None, product_type_external_id: int = None) -> list[OzonCharacteristic]:
        if not self._characteristics:
            self._fetch_characteristics(external_category_id, product_type_external_id)

        return self._characteristics

    def get_characteristic_values(self) -> list[OzonCharacteristicValue]:
        if not self._characteristic_values:
            self._fetch_characteristic_values()

        return self._characteristic_values

    def _fetch_categories(self):
        self._categories = self._get_categories_from_ozon()

    def _get_categories_from_ozon(self) -> list[OzonCategory]:
        """Возвращает пару списков DTO категорий и типов товаров OZON."""

        response = self._send_category_request()
        raw_categories = response.get('result')

        return self._unpack_categories(raw_categories)

    def _send_category_request(self) -> dict:
        """Возвращает ответ на запрос получения категорий."""

        try:
            response = requests.post(config.ozon_categories_url, headers=self._get_headers()).json()
        except (requests.ConnectionError, requests.ConnectTimeout):
            response = self._send_category_request()

        return response

    def _unpack_categories(self, raw_categories: list[dict], parent_id: int = None) -> list[OzonCategory]:
        """Распаковка дерева категорий и десериализация в DTO."""

        categories = []

        for raw_category in raw_categories:
            if category_id := raw_category.get('description_category_id'):
                category = OzonCategory(
                    description_category_id=category_id,
                    category_name=raw_category.get('category_name'),
                    parent_id=parent_id,
                )
                categories.append(category)
                children_categories = self._unpack_categories(
                    raw_category.get('children'),
                    category.description_category_id,
                )

                categories.extend(children_categories)
            else:
                product_type = OzonCategory(
                    description_category_id=raw_category.get('type_id'),
                    category_name=raw_category.get('type_name'),
                    parent_id=parent_id,
                )
                categories.append(product_type)

        return categories

    def _fetch_characteristics(self, external_category_id: int, product_type_external_id: int):
        self._characteristics = self._get_characteristics_from_ozon(external_category_id, product_type_external_id)

    def _get_characteristics_from_ozon(self, external_category_id: int, product_type_external_id: int) -> list[OzonCharacteristic]:
        """Возвращает список из DTO характеристик OZON."""

        body = dict(description_category_id=external_category_id, type_id=product_type_external_id)

        response = requests.post(config.ozon_characteristics_url, json=body, headers=self._get_headers())
        characteristics = response.json().get('result')

        return self._unpack_characteristics(characteristics, external_category_id, product_type_external_id)

    @staticmethod
    def _unpack_characteristics(
            raw_characteristics: list[dict],
            description_category_id: int,
            type_id: int,
    ) -> list[OzonCharacteristic]:
        """Десериализует данные характеристик в DTO."""

        result = []

        for raw_characteristic in raw_characteristics:
            raw_characteristic['description_category_id'] = description_category_id
            raw_characteristic['type_id'] = type_id

            characteristic = OzonCharacteristic.from_dict(raw_characteristic)

            if characteristic.id == config.ozon_product_type_characteristic_id:
                continue

            # TODO: Придумать иное решение, но пока эти характеристики заполняет программа, а не администратор
            not_required_characteristic_ids = (
                config.ozon_brand_characteristic_id,
                config.ozon_model_name_characteristic_id,
                config.ozon_name_characteristic_id,
                config.ozon_image_characteristic_id,
            )
            if characteristic.id in not_required_characteristic_ids:
                characteristic.is_required = False

            result.append(characteristic)

        return result

    def _fetch_characteristic_values(self):
        self._characteristic_values = self._get_characteristic_values_from_ozon()

    def _get_characteristic_values_from_ozon(self) -> list[OzonCharacteristicValue]:
        """Возвращает список из DTO значений характеристик OZON."""

        characteristic_values = []

        for characteristic in self.get_characteristics():
            characteristic_values.extend(self._get_characteristic_values_by_characteristic(characteristic))

        return characteristic_values

    # TODO: Исправить метод по DRY
    def _get_characteristic_values_by_characteristic(self, characteristic: OzonCharacteristic) -> list[OzonCharacteristicValue]:
        values = []

        # TODO: Придумать другое решение, но пока просто не загружаем значения брендов, т.к. их очень много
        if characteristic.dictionary_id and characteristic.id not in (
            config.ozon_brand_characteristic_id, 
            config.ozon_product_type_characteristic_id
        ):
            body = dict(
                attribute_id=characteristic.id,
                description_category_id=characteristic.description_category_id,
                type_id=characteristic.type_id,
                limit=5000,
            )

            response = self._send_characteristic_value_request(body)
            response_values = response.get('result')

            for raw_value in response_values:
                raw_value['attribute_id'] = characteristic.id
                value = OzonCharacteristicValue.from_dict(raw_value)

                values.append(value)

            while response.get('has_next'):
                last_value_id = response_values[-1].get('id')
                body['last_value_id'] = last_value_id

                response = self._send_characteristic_value_request(body)
                response_values = response.get('result')

                for raw_value in response_values:
                    raw_value['attribute_id'] = characteristic.id
                    value = OzonCharacteristicValue.from_dict(raw_value)

                    values.append(value)

        return values

    def get_brand_values(self, product_type_external_id: int, category_external_id: int) -> list[OzonCharacteristicValue]:
        values = []

        body = dict(
            attribute_id=config.ozon_brand_characteristic_id,
            description_category_id=category_external_id,
            type_id=product_type_external_id,
            limit=5000,
        )

        response = self._send_characteristic_value_request(body)
        response_values = response.get('result')

        for raw_value in response_values:
            raw_value['attribute_id'] = config.ozon_brand_characteristic_id
            value = OzonCharacteristicValue.from_dict(raw_value)

            values.append(value)

        while response.get('has_next'):
            last_value_id = response_values[-1].get('id')
            body['last_value_id'] = last_value_id

            response = self._send_characteristic_value_request(body)
            response_values = response.get('result')

            for raw_value in response_values:
                raw_value['attribute_id'] = config.ozon_brand_characteristic_id
                value = OzonCharacteristicValue.from_dict(raw_value)

                values.append(value)

        return values

    def _send_characteristic_value_request(self, body: dict):
        """Возвращает ответ на запрос получения характеристик, исходя из параметров в body."""

        try:
            response = requests.post(config.ozon_characteristic_values_url, json=body, headers=self._get_headers()).json()
        except (requests.ConnectionError, requests.ConnectTimeout):
            response = self._send_characteristic_value_request(body)

        return response

    def _get_headers(self):
        if not self._headers:
            client_id = get_ozon_client_id()
            ozon_api_key = get_ozon_api_key()
            self._headers = {'Client-Id': client_id, 'Api-Key': ozon_api_key}

        return self._headers
