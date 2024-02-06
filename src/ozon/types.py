from dataclasses import (
    dataclass,
)


@dataclass
class OzonCategory:
    """DTO категорий OZON."""

    description_category_id: int
    category_name: str
    parent_id: int | None = None


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
    description_category_id: int
    type_id: int
    max_value_count: int
    attribute_complex_id: int


@dataclass
class OzonCharacteristicValue:
    """DTO значений характеристик OZON."""

    id: int
    value: str | int
    attribute_id: int
    info: str | None = None
    picture: str | None = None
