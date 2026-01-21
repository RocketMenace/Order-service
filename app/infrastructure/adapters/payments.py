from ..config.settings import Settings
from .httpx_client import BaseHTTPXClient
from fastapi import status
from .contracts import PaymentRequest


class PaymentsService:
    def __init__(self, client: BaseHTTPXClient, settings: Settings):
        self.client = client
        self.base_url = settings.api_payments_service
        self.access_token = settings.access_token
        self.callback_url = settings.payments_callback_url

    async def create_payment(self, payload: PaymentRequest) -> bool:
        payload["callback_url"] = self.callback_url
        async with self.client as client:
            response = await client.post(
                url=self.base_url,
                # headers={"Authorization": f"Bearer {self.access_token}"},
                headers={"X-API-Key": self.access_token},
                json=payload,
            )
            if response.status_code != status.HTTP_201_CREATED:
                return False
            return True
