from .base import DomainError
from uuid import UUID


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
    def __init__(self):
        message = "Order in process."
        super().__init__(message)
