from dataclasses import dataclass, asdict
from uuid import UUID

from ..enums.events import EventTypeEnum, OutboxEventStatusEnum
from typing import Any
from ..interfaces.contracts import (
    NotificationRequest,
    PaymentRequest,
    BrokerMessageRequest,
)


@dataclass
class OutboxDTO:
    event_type: EventTypeEnum
    payload: NotificationRequest | PaymentRequest | BrokerMessageRequest
    status: OutboxEventStatusEnum

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OutboxDTOResponse:
    id: UUID
    event_type: EventTypeEnum
    payload: dict[str, Any]
    status: OutboxEventStatusEnum

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
