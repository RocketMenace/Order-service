from decimal import Decimal

from app.core.value_objects.item import Item


class Order:
    def __init__(self, qty: int, item: Item, user_id: str):
        self.qty = qty
        self.item = item
        self.user_id = user_id
        self.allocations = set()

    def allocate(self, item: Item) -> None:
        if self.can_allocate():
            self.allocations.add(item)

    def can_allocate(self) -> bool:
        return self.item.available_qty >= self.qty

    def calculate_amount(self, price: Decimal) -> Decimal | None:
        if self.can_allocate():
            return self.qty * price
        return None
