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

        formatted_and_merged_categories: dict[int, MBCategory] = {}

        for category in raw_categories:
            if category.category_id not in formatted_and_merged_categories:
                formatted_category = cls._format_category(category)
                formatted_and_merged_categories[category.category_id] = formatted_category
            else:
                formatted_category = formatted_and_merged_categories[category.category_id]

                if category.parent_category_id:
                    formatted_category.parent_category_external_ids.append(category.parent_category_id)

        return list(formatted_and_merged_categories.values())

    @classmethod
    def _format_category(cls, category: OzonCategory) -> MBCategory:
        args = [
            category.category_id,
            category.category_name,
            config.marketplace_id,
        ]

        if parent_id := category.parent_category_id:
            args.append([parent_id])

        formatted_category = MBCategory(*args)

        return formatted_category

    @classmethod
    def format_characteristics(cls, raw_characteristics: list[OzonCharacteristic]) -> list[MBCharacteristic]:
        """Форматирует характеристики озона под шаблон MB характеристик.

        Метод также сливает повторяющиеся озон характеристики из списка raw_characteristics.
        У них могут отличаться лишь категории. Поэтому если характеристику уже отформатировали,
        то пополняем список связанных категорий.
        """

        formatted_and_merged_characteristics: dict[int, MBCharacteristic] = {}

        for characteristic in raw_characteristics:
            if characteristic.id not in formatted_and_merged_characteristics:
                formatted_characteristic = cls._format_characteristic(characteristic)
                formatted_and_merged_characteristics[characteristic.id] = formatted_characteristic
            else:
                formatted_characteristic = formatted_and_merged_characteristics[characteristic.id]
                formatted_characteristic.category_external_ids.append(characteristic.category_id)

        return list(formatted_and_merged_characteristics.values())

    @staticmethod
    def _format_characteristic(characteristic: OzonCharacteristic) -> MBCharacteristic:
        formatted_characteristic = MBCharacteristic(
            characteristic.id,
            characteristic.name,
            characteristic.is_required,
            config.marketplace_id,
            [characteristic.product_type_id],
        )

        return formatted_characteristic

    @classmethod
    def format_characteristic_values(cls, raw_values: list[OzonCharacteristicValue]) -> list[MBCharacteristicValue]:
        """Форматирует значения характеристик озона под шаблон MB значений."""

        result = []

        for value in raw_values:
            formatted_value = cls._format_characteristic_value(value)
            result.append(formatted_value)

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

    @staticmethod
    def _send_object(obj, url, name, display_field):
        response = requests.post(url, json=vars(obj))
        display_value = getattr(obj, display_field)

        if response.status_code == 201:
            print(f'The "{display_value}" {name} has been created.')
        elif response.status_code == 200:
            print(f'The "{display_value}" {name} already exists.')
        else:
            print(f'When creating the "{display_value}" {name}, the server returned an error.')


class Fetcher:
    """Забирает данные с Markets-Bridge."""

    def get_existed_characteristic_value_ids(self) -> set[int]:
        return {value['external_id'] for value in self.get_characteristic_values()}

    def get_characteristic_values(self):
        values = requests.get(config.mb_characteristic_values_url).json()

        return values