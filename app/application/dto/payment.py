from dataclasses import dataclass, asdict
from uuid import UUID
from decimal import Decimal
from typing import Any
from datetime import datetime


@dataclass
class PaymentDTO:
    order_id: UUID
    amount: Decimal
    idempotency_key: UUID
    id: UUID | None = None
    user_id: UUID | None = None
    status: str | None = None
    created_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, Decimal):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
