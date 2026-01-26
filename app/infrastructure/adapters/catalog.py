from decimal import Decimal
from typing import Any
from uuid import UUID

from adaptix import Retort, loader
from fastapi import status

from app.core.value_objects.item import Item
from app.infrastructure.adapters.httpx_client import BaseHTTPXClient
from app.infrastructure.config.logging import get_logger
from app.infrastructure.config.settings import Settings

logger = get_logger(__name__)


class CatalogService:
    def __init__(self, client: BaseHTTPXClient, settings: Settings):
        self.client = client
        self.base_url = settings.api_catalog_service
        self.access_token = settings.access_token

    async def get_item_stock(self, item_id: UUID) -> Item | None:
        async with self.client as client:
            response = await client.get(
                url=f"{self.base_url}/{item_id}",
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
