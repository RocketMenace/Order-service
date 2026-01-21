from ..value_objects.item import Item


class Order:
    def __init__(self, qty: int, item: Item, user_id: str):
        self.qty = qty
        self.item = item
        self.user_id = user_id
        self.allocations = set()

    async def allocate(self, item: Item) -> None:
        if self.can_allocate():
            self.allocations.add(item)

    def can_allocate(self) -> bool:
        return self.item.available_qty >= self.qty
