from typing import Protocol, Self
from .repository import (
    OrderRepositoryProtocol,
    OutboxRepositoryProtocol,
    OrderStatusRepositoryProtocol,
    InboxRepositoryProtocol,
    NotificationRepositoryProtocol,
)


class UnitOfWorkProtocol(Protocol):
    orders: OrderRepositoryProtocol
    outbox: OutboxRepositoryProtocol
    order_status: OrderStatusRepositoryProtocol
    inbox: InboxRepositoryProtocol
    notifications: NotificationRepositoryProtocol

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
