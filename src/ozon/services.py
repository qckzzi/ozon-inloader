import requests

import config
from ozon.types import (
    OzonCategory,
    OzonCharacteristic,
    OzonCharacteristicValue,
)


class Fetcher:
    """Сборщик данных OZON.

    Собирает и хранит в себе атрибуты внешней системы. Возвращает их в таком виде, в каком и получил.
    """

    headers = {
        'Client-Id': config.ozon_client_id,
        'Api-Key': config.ozon_api_key,
    }

    def __init__(self):
        self._categories: list[OzonCategory] = []
        self._characteristics: list[OzonCharacteristic] = []
        self._characteristic_values: list[OzonCharacteristicValue] = []

    def get_categories(self) -> list[OzonCategory]:
        if not self._categories:
            self._fetch_categories()

        return self._categories

    def get_characteristics(self, external_category_id: int = None) -> list[OzonCharacteristic]:
        if not self._characteristics:
            self._fetch_characteristics(external_category_id)

        return self._characteristics

    def get_characteristic_values(self) -> list[OzonCharacteristicValue]:
        if not self._characteristic_values:
            self._fetch_characteristic_values()

        return self._characteristic_values

    def _fetch_categories(self):
        self._categories = self._get_categories_from_ozon()

    def _get_categories_from_ozon(self) -> list[OzonCategory]:
        """Возвращает список DTO категорий OZON."""

        response = self._send_category_request()
        raw_categories = response.get('result')

        categories = self._unpack_categories(raw_categories)

        return categories

    def _send_category_request(self) -> dict:
        """Возвращает ответ на запрос получения категорий."""

        try:
            response = requests.post(config.ozon_categories_url, headers=self.headers).json()
        except (requests.ConnectionError, requests.ConnectTimeout):
            response = self._send_category_request()

        return response

    def _unpack_categories(self, raw_categories: list[dict], parent_id: int = None) -> list[OzonCategory]:
        """Распаковка дерева категорий и десериализация в DTO."""

        result = []

        for raw_category in raw_categories:
            category = OzonCategory(
                category_id=raw_category.get('category_id'),
                title=raw_category.get('title'),
                parent_id=parent_id,
            )
            result.append(category)

            if children := raw_category.get('children'):
                parent_id = category.category_id
                result.extend(self._unpack_categories(children, parent_id))

        return result

    def _fetch_characteristics(self, external_category_id: int | None):
        self._characteristics = self._get_characteristics_from_ozon(external_category_id)

    def _get_characteristics_from_ozon(self, external_category_id: int | None) -> list[OzonCharacteristic]:
        """Возвращает список из DTO характеристик OZON."""

        if external_category_id:
            relevant_categories = [{'external_id': external_category_id}]
        else:
            relevant_categories = requests.get(config.mb_relevant_categories_url).json()

        result = []

        for category in relevant_categories:

            category_id = category.get('external_id')

            body = dict(category_id=[category_id])

            response = requests.post(config.ozon_characteristics_url, json=body, headers=self.headers)
            response_json = response.json().get('result')

            for characteristics_data in response_json:
                raw_characteristics = characteristics_data.get('attributes')
                category_id = characteristics_data.get('category_id')
                result.extend(self._unpack_characteristics(raw_characteristics, category_id))

        return result

    @staticmethod
    def _unpack_characteristics(
            raw_characteristics: list[dict],
            category_id: int,
    ) -> list[OzonCharacteristic]:
        """Десериализует данные характеристик в DTO."""

        result = []

        for raw_characteristic in raw_characteristics:
            raw_characteristic['category_id'] = category_id

            characteristic = OzonCharacteristic(**raw_characteristic)

            # TODO: Придумать иное решение, но пока эти 2 характеристики заполняет программа, а не администратор
            if characteristic.id in (config.ozon_brand_characteristic_id, config.ozon_model_name_characteristic_id):
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
        if characteristic.dictionary_id and characteristic.id != config.ozon_brand_characteristic_id:
            body = dict(
                attribute_id=characteristic.id,
                category_id=characteristic.category_id,
                limit=5000,
            )

            response = self._send_characteristic_value_request(body)
            response_values = response.get('result')

            for raw_value in response_values:
                raw_value['attribute_id'] = characteristic.id
                value = OzonCharacteristicValue(**raw_value)

                values.append(value)

            while response.get('has_next'):
                last_value_id = response_values[-1].get('id')
                body['last_value_id'] = last_value_id

                response = self._send_characteristic_value_request(body)
                response_values = response.get('result')

                for raw_value in response_values:
                    raw_value['attribute_id'] = characteristic.id
                    value = OzonCharacteristicValue(**raw_value)

                    values.append(value)

        return values

    def _send_characteristic_value_request(self, body: dict):
        """Возвращает ответ на запрос получения характеристик, исходя из параметров в body."""

        try:
            response = requests.post(config.ozon_characteristic_values_url, json=body, headers=self.headers).json()
        except (requests.ConnectionError, requests.ConnectTimeout):
            response = self._send_characteristic_value_request(body)

        return response
