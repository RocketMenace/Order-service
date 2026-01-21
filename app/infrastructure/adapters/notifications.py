from ..config.settings import Settings
from .httpx_client import BaseHTTPXClient
from .contracts import NotificationRequest
from fastapi import status


class NotificationsService:
    def __init__(self, client: BaseHTTPXClient, settings: Settings):
        self.client = client
        self.base_url = settings.api_notifications_service
        self.access_token = settings.access_token

    async def send_notification(self, payload: NotificationRequest) -> bool:
        async with self.client as client:
            response = await client.post(
                url=self.base_url,
                headers={"X-API-Key": self.access_token},
                json=payload,
            )
            if response.status_code != status.HTTP_201_CREATED:
                return False
            return True
