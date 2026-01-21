from ..interfaces.uow import UnitOfWorkProtocol
from ..enums.events import InboxEventStatusEnum, EventTypeEnum, OrderStatusEnum
from ..dto.order import OrderStatusDTO


class UpdateOrderStatusUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def __call__(self) -> None:
        async with self.uow:
            events = await self.uow.inbox.get_events(
                status=InboxEventStatusEnum.PENDING
            )
            if not events:
                return None
            for event in events:
                if event.event_type == EventTypeEnum.ORDER_PAID:
                    order_status_dto = OrderStatusDTO(
                        order_id=event.payload.get("order_id"),
                        status=OrderStatusEnum.PAID,
                    )
                    await self.uow.order_status.create(entity=order_status_dto)
                    await self.uow.inbox.mark_as_processed(event_id=event.id)
                    await self.uow.commit()
                if event.event_type == EventTypeEnum.ORDER_CANCELLED:
                    order_status_dto = OrderStatusDTO(
                        order_id=event.payload.get("order_id"),
                        status=OrderStatusEnum.CANCELLED,
                    )
                    await self.uow.order_status.create(entity=order_status_dto)
                    await self.uow.inbox.mark_as_processed(event_id=event.id)
                    await self.uow.commit()
            return None
