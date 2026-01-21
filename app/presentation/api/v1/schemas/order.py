from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from .enums import OrderStatusEnum
from app.application.dto.order import OrderDTO


class OrderBaseSchema(BaseModel):
    quantity: int = Field(
        default=1,
        description="Item quantity",
        ge=1,
        examples=[
            1,
        ],
    )
    item_id: UUID = Field(
        ...,
        description="Item valid UUID",
        examples=[
            "de71f1c7-674d-4569-ad05-5f1367ccc4ce",
        ],
    )


class OrderRequestSchema(OrderBaseSchema):
    user_id: str = Field(
        ...,
        description="User ID",
        frozen=True,
        examples=[
            "977b8dfe-91aa-4ea7-bcda-cedf40ea92a4",
        ],
    )
    idempotency_key: UUID = Field(
        ...,
        description="Idempotency key",
        frozen=True,
        examples=[
            "64104164-5683-4d48-979d-37d32ecce6fd",
        ],
    )

    def to_dto(self) -> OrderDTO:
        return OrderDTO(
            user_id=self.user_id,
            idempotency_key=self.idempotency_key,
            quantity=self.quantity,
            item_id=self.item_id,
        )


class OrderResponseSchema(OrderBaseSchema):
    id: UUID = Field(
        ...,
        description="Order ID",
        frozen=True,
        examples=[
            "9a4f56ba-1979-4fd1-a16e-b0727c472173",
        ],
    )
    status: OrderStatusEnum = Field(
        default=OrderStatusEnum.NEW,
        description="Order status",
        examples=[
            OrderStatusEnum.NEW,
        ],
    )
    created_at: datetime = Field(
        ...,
        description="Order created at time",
        frozen=True,
        examples=[
            "2025-10-31T14:12:57.868385+00:00",
        ],
    )
    updated_at: datetime = Field(
        ...,
        description="Order updated at time",
        examples=[
            "2025-10-31T14:12:57.868385+00:00",
        ],
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
