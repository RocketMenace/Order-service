from dataclasses import asdict, dataclass
from typing import Any
from uuid import UUID

from app.application.enums.events import EventTypeEnum, InboxEventStatusEnum


@dataclass
class InboxDTO:
    event_type: EventTypeEnum
    payload: dict[str, Any]
    status: InboxEventStatusEnum
    idempotency_key: UUID

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InboxDTOResponse:
    id: UUID
    event_type: EventTypeEnum
    payload: dict[str, Any]
    status: InboxEventStatusEnum
    idempotency_key: UUID

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
