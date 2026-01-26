from datetime import datetime
from typing import TypedDict
from uuid import UUID

from app.core.enums.order import OrderStatusEnum


class OrderResponseData(TypedDict):
    id: UUID
    quantity: int
    item_id: UUID
    status: OrderStatusEnum
    created_at: datetime
    updated_at: datetime
