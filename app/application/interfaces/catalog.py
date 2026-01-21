from typing import Protocol
from uuid import UUID
from app.core.value_objects.item import Item


class CatalogServiceProtocol(Protocol):
    async def get_item_stock(self, item_id: UUID) -> Item: ...
