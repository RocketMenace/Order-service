from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal


@dataclass(frozen=True, kw_only=True, slots=True, repr=False)
class Item:
    id: UUID
    name: str
    price: Decimal
    available_qty: int
