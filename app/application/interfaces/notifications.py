from typing import Protocol
from .contracts import NotificationRequest


class NotificationsServiceProtocol(Protocol):
    async def send_notification(self, payload: NotificationRequest) -> bool: ...
