import uuid

from app.application.dto import InboxDTO, OutboxDTO
from app.application.enums.events import (EventTypeEnum, InboxEventStatusEnum,
                                          OrderStatusEnum,
                                          OutboxEventStatusEnum)
from app.application.interfaces import NotificationRequest, UnitOfWorkProtocol
from app.application.interfaces.contracts import BrokerMessageResponse


class ShippingResponseUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def __call__(self, message: BrokerMessageResponse) -> None:
        if not message:
            return None

        async with self.uow:
            if await self.uow.inbox.get_event(
                idempotency_key=uuid.UUID(message.get("order_id"))
            ):
                return None
            event_type = message.get("event_type")
            if event_type == EventTypeEnum.ORDER_SHIPPED:
                inbox_dto = InboxDTO(
                    event_type=EventTypeEnum.ORDER_SHIPPED,
                    status=InboxEventStatusEnum.PENDING,
                    idempotency_key=uuid.UUID(message.get("order_id")),
                    payload={
                        "order_id": uuid.UUID(message.get("order_id")),
                        "status": OrderStatusEnum.SHIPPED,
                    },
                )
                outbox_dto = OutboxDTO(
                    event_type=EventTypeEnum.ORDER_SHIPPED,
                    status=OutboxEventStatusEnum.PENDING,
                    payload=NotificationRequest(
                        message=f"Order has been shipped",
                        idempotency_key=str(uuid.uuid4()),
                    ),
                )
            else:
                inbox_dto = InboxDTO(
                    event_type=EventTypeEnum.ORDER_CANCELLED,
                    status=InboxEventStatusEnum.PENDING,
                    idempotency_key=uuid.UUID(message.get("order_id")),
                    payload={
                        "order_id": uuid.UUID(message.get("order_id")),
                        "status": OrderStatusEnum.CANCELLED,
                    },
                )
                outbox_dto = OutboxDTO(
                    event_type=EventTypeEnum.ORDER_CANCELLED,
                    status=OutboxEventStatusEnum.PENDING,
                    payload=NotificationRequest(
                        message=f"Order has been cancelled",
                        idempotency_key=str(uuid.uuid4()),
                    ),
                )

            await self.uow.inbox.create(entity=inbox_dto)
            await self.uow.outbox.create(entity=outbox_dto)
            await self.uow.commit()

            return None
