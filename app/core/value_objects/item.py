from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, kw_only=True, slots=True, repr=False)
class Item:
    id: UUID
    name: str
    price: Decimal
    available_qty: int
