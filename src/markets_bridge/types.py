from dataclasses import (
    dataclass,
    field,
)


@dataclass
class MBCategory:
    external_id: int
    name: str
    marketplace_id: int
    parent_category_external_ids: list[int] = field(default_factory=list)


@dataclass
class MBCharacteristic:
    external_id: int
    name: str
    is_required: bool
    marketplace_id: int
    category_external_ids: list[int] = field(default_factory=list)


@dataclass
class MBCharacteristicValue:
    external_id: int
    value: str
    marketplace_id: int
    characteristic_external_id: int
