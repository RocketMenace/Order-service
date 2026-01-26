from app.application.enums.events import EventTypeEnum, OutboxEventStatusEnum
from app.application.interfaces import (PaymentRequest, PaymentServiceProtocol,
                                        UnitOfWorkProtocol)


class CreatePaymentUseCase:
    def __init__(
        self, uow: UnitOfWorkProtocol, payments_service: PaymentServiceProtocol
    ):
        self.uow = uow
        self.payment_service = payments_service

    async def __call__(self) -> None:
        async with self.uow:
            events = await self.uow.outbox.get_events(
                event_type=EventTypeEnum.PAYMENT_REQUESTED,
                status=OutboxEventStatusEnum.PENDING,
            )
            if not events:
                return None
            for event in events:
                payload = PaymentRequest(
                    order_id=event.payload.get("order_id"),
                    amount=event.payload.get("amount"),
                    idempotency_key=event.payload.get("idempotency_key"),
                )
                if await self.payment_service.create_payment(payload=payload):
                    await self.uow.outbox.mark_as_sent(event_id=event.id)
                    await self.uow.commit()
            return None
