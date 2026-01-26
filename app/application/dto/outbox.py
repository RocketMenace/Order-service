from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any
from uuid import UUID

from app.application.enums.events import EventTypeEnum, OutboxEventStatusEnum

if TYPE_CHECKING:
    from app.application.interfaces.contracts import (BrokerMessageRequest,
                                                      NotificationRequest,
                                                      PaymentRequest)


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
