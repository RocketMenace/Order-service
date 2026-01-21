from dataclasses import dataclass, asdict

from uuid import UUID
from ..interfaces.contracts import NotificationRequest


@dataclass
class NotificationDTO:
    payload: NotificationRequest
    sent: bool

    def to_dict(self):
        return asdict(self)


@dataclass
class NotificationDTOResponse:
    id: UUID
    payload: NotificationRequest
    sent: bool
