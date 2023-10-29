from dataclasses import (
    dataclass,
)


@dataclass
class OzonCategory:
    """DTO категорий OZON."""

    category_id: int
    category_name: str
    disabled: bool
    parent_category_id: int = None


@dataclass
class OzonCharacteristic:
    """DTO характеристик OZON."""

    id: int
    name: str
    description: str
    type: str
    is_collection: bool
    is_required: bool
    is_aspect: bool
    group_name: str
    group_id: int
    dictionary_id: int
    product_type_id: int
    category_id: int


@dataclass
class OzonCharacteristicValue:
    """DTO значений характеристик OZON."""

    id: int
    value: str
    info: str
    picture: str
    attribute_id: int
