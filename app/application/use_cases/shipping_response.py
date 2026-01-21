import uuid
from typing import Any

from aiokafka.structs import ConsumerRecord

from ..interfaces.uow import UnitOfWorkProtocol
from ..dto.inbox import InboxDTO
from ..dto.outbox import OutboxDTO
from ..interfaces.contracts import NotificationRequest
from ..enums.events import (
    EventTypeEnum,
    InboxEventStatusEnum,
    OutboxEventStatusEnum,
)


class ShippingResponseUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def __call__(self, message: ConsumerRecord) -> None:
        if not message.value:
            return None



        shipment_id = message_data.get("shipment_id")
        order_id = message_data.get("order_id", "")
        
        if shipment_id:
            idempotency_key = uuid.uuid5(uuid.NAMESPACE_DNS, f"shipping-{shipment_id}")
        elif order_id:
            idempotency_key = uuid.uuid5(uuid.NAMESPACE_DNS, f"shipping-{order_id}")
        else:
            return None

        async with self.uow:
            existing_event = await self.uow.inbox.get_event(idempotency_key=idempotency_key)
            if existing_event:
                return None  #

            inbox_dto = InboxDTO(
                event_type=EventTypeEnum.ORDER_SHIPPED,
                status=InboxEventStatusEnum.PENDING,
                idempotency_key=idempotency_key,
                payload=message_data,
            )

            outbox_dto = OutboxDTO(
                event_type=EventTypeEnum.ORDER_SHIPPED,
                status=OutboxEventStatusEnum.PENDING,
                payload=NotificationRequest(
                    message=f"Order {order_id} has been shipped",
                    idempotency_key=str(uuid.uuid4()),
                ),
            )

            await self.uow.inbox.create(entity=inbox_dto)
            await self.uow.outbox.create(entity=outbox_dto)
            await self.uow.commit()

            return None
