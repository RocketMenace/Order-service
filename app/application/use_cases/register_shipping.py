from ..interfaces.uow import UnitOfWorkProtocol
from ..interfaces.message_broker import MessageProducerProtocol
from ..enums.events import OutboxEventStatusEnum, EventTypeEnum
from ..interfaces.contracts import BrokerMessageRequest


class RegisterShippingUseCase:
    def __init__(self, uow: UnitOfWorkProtocol, broker: MessageProducerProtocol):
        self.uow = uow
        self.broker = broker

    async def __call__(self) -> None:
        async with self.uow:
            messages = await self.uow.outbox.get_events(
                event_type=EventTypeEnum.SHIPPING_REQUESTED,
                status=OutboxEventStatusEnum.PENDING,
            )
            if not messages:
                return None
        async with self.broker:
            for message in messages:
                async with self.uow as uow:
                    try:
                        await self.broker.publish_message(
                            message=BrokerMessageRequest(
                                event_type=message.payload.get("event_type"),
                                order_id=message.payload.get("order_id"),
                                item_id=message.payload.get("item_id"),
                                quantity=message.payload.get("quantity"),
                                idempotency_key=message.payload.get("idempotency_key"),
                            )
                        )
                    except Exception as e:
                        print(e)

                    await uow.outbox.mark_as_sent(event_id=message.id)
                    await uow.commit()
            return None
