from dataclasses import asdict, dataclass
from decimal import Decimal
from uuid import UUID

from ..enums.events import OrderStatusEnum


@dataclass
class OrderDTO:
    user_id: str
    idempotency_key: UUID
    quantity: int
    item_id: UUID
    amount: Decimal | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class OrderDTOResponse:
    user_id: str
    idempotency_key: str
    quantity: int
    item_id: str
    id: UUID
    created_at: str
    updated_at: str
    amount: Decimal | None = None    def to_dict(self):
        data = asdict(self)
        for k, v in data.items():
            if isinstance(v, Decimal):
                data[k] = str(v)
            if isinstance(v, UUID):
                data[k] = str(v)
        return data
@dataclass
class OrderStatusDTO:
    order_id: UUID
    status: OrderStatusEnum | None = None

    def to_dict(self):
        data = asdict(self)
        for k, v in data.items():
            if isinstance(v, UUID):
                data[k] = str(v)
        return data
