from dataclasses import (
    dataclass,
    field,
)


@dataclass
class MBCategory:
    external_id: int
    name: str
    marketplace_id: int
    parent_category_external_id: int | None = None


@dataclass
class MBCharacteristic:
    external_id: int
    name: str
    description: str
    is_required: bool
    has_reference_values: bool
    marketplace_id: int
    category_external_id: int


@dataclass
class MBCharacteristicValue:
    external_id: int
    value: str
    marketplace_id: int
    characteristic_external_id: int
