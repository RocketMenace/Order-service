from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.application.dto.payment import PaymentDTO

from .enums import PaymentStatusEnum


class PaymentRequestSchema(BaseModel):
    id: UUID = Field(
        ...,
        description="Payment ID",
        frozen=True,
        examples=[
            "977b8dfe-91aa-4ea7-bcda-cedf40ea92a4",
        ],
    )
    user_id: UUID = Field(
        ...,
        description="User ID",
        frozen=True,
        examples=[
            "977b8dfe-91aa-4ea7-bcda-cedf40ea92a4",
        ],
    )
    order_id: UUID = Field(
        ...,
        description="Order ID",
        frozen=True,
        examples=[
            "977b8dfe-91aa-4ea7-bcda-cedf40ea92a4",
        ],
    )
    amount: Decimal = Field(
        ...,
        description="Amount to pay",
        examples=[
            "2.50",
        ],
    )
    status: PaymentStatusEnum = Field(
        default="pending",
        description="Payment status",
        examples=[
            "pending",
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
    created_at: datetime = Field(
        ...,
        description="Payment created at time",
        frozen=True,
        examples=[
            "2025-10-31T14:12:57.868385+00:00",
        ],
    )

    def to_dto(self) -> PaymentDTO:
        return PaymentDTO(
            order_id=self.order_id,
            amount=self.amount,
            idempotency_key=self.idempotency_key,
            id=self.id,
            user_id=self.user_id,
            status=self.status,
            created_at=self.created_at,
        )
