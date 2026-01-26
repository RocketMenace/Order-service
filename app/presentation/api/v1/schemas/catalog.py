from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CatalogResponseSchema(BaseModel):
    id: UUID = Field(
        ...,
        description="Item UUID",
        examples=[
            "a8dea023-6f6b-451b-a957-e5f81a7021a5",
        ],
    )
    name: str = Field(
        ...,
        description="Item name",
        examples=[
            "Brown chair",
        ],
    )
    price: Decimal = Field(
        ...,
        description="Item price",
        examples=[
            "2.50",
        ],
    )
    available_qty: int = Field(
        ...,
        description="Item available quantity",
        examples=[
            10,
        ],
    )
    created_at: datetime = Field(
        ...,
        description="Item created at time",
        examples=[
            "2024-01-01T00:00:00Z",
        ],
    )
