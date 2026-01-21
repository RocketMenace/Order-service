from sqlalchemy.ext.asyncio import AsyncSession
from typing import Self

from .repositories.inbox import InboxRepository
from .repositories.order import OrderRepository
from .repositories.outbox import OutboxRepository
from .repositories.order_status import OrderStatusRepository
from .repositories.notification import NotificationRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._orders: OrderRepository | None = None
        self._outbox: OutboxRepository | None = None
        self._inbox: InboxRepository | None = None
        self._order_status: OrderStatusRepository | None = None
        self._notifications: NotificationRepository | None = None

    @property
    def order_status(self) -> OrderStatusRepository:
        if self._order_status is None:
            self._order_status = OrderStatusRepository(session=self.session)
        return self._order_status

    @property
    def orders(self) -> OrderRepository:
        if self._orders is None:
            self._orders = OrderRepository(session=self.session)
        return self._orders

    @property
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            self._outbox = OutboxRepository(session=self.session)
        return self._outbox

    @property
    def inbox(self) -> InboxRepository:
        if self._inbox is None:
            self._inbox = InboxRepository(session=self.session)
        return self._inbox

    @property
    def notifications(self) -> NotificationRepository:
        if self._notifications is None:
            self._notifications = NotificationRepository(session=self.session)
        return self._notifications

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
