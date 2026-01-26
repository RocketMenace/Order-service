from uuid import UUID

from app.core.exceptions.base import DomainError
from app.core.exceptions.contracts import OrderResponseData


class ItemNotFoundError(DomainError):
    def __init__(self, item_id: UUID):
        self.item_id = item_id
        message = f"Item with {item_id} not found."
        super().__init__(message)


class NotEnoughStocksError(DomainError):
    def __init__(self):
        message = "Item is out of stock. Not enough quantity available."
        super().__init__(message)


class OrderAlreadyExistsError(DomainError):
    def __init__(self, data: OrderResponseData):
        self.data = data
        super().__init__()
