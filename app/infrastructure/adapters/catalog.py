from uuid import UUID
from app.core.value_objects.item import Item
from ..config.settings import Settings
from typing import Any
from adaptix import Retort, loader
from decimal import Decimal
from .httpx_client import BaseHTTPXClient
from fastapi import status


class CatalogService:
    def __init__(self, client: BaseHTTPXClient, settings: Settings):
        self.client = client
        self.base_url = settings.api_catalog_service
        self.access_token = settings.access_token

    async def get_item_stock(self, item_id: UUID) -> Item | None:
        async with self.client as client:
            response = await client.get(
                url=f"{self.base_url}/{item_id}",
                # headers={"Authorization": f"Bearer {self.access_token}"},
                headers={"X-API-Key": self.access_token},
            )
            if response.status_code != status.HTTP_200_OK:
                return None
            return self._to_value_object(response.json())

    def _to_value_object(self, data: dict[str, Any]) -> Item:
        self._retort = Retort(
            recipe=[
                loader(Decimal, lambda x: Decimal(str(x))),
                loader(UUID, lambda x: UUID(str(x))),
            ]
        )
        return self._retort.load(data, Item)
