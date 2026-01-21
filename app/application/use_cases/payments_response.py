import uuid

from ..dto.outbox import OutboxDTO
from ..dto.inbox import InboxDTO
from ..interfaces.uow import UnitOfWorkProtocol
from ..dto.payment import PaymentDTO
from ..interfaces.contracts import NotificationRequest
from ..enums.events import (
    PaymentStatusEnum,
    InboxEventStatusEnum,
    EventTypeEnum,
    OutboxEventStatusEnum
)


class HandlePaymentResponseUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def __call__(self, payment: PaymentDTO) -> None:
        async with self.uow:
            if await self.uow.inbox.get_event(idempotency_key=payment.idempotency_key):
                return  # status code 200
            if payment.status == PaymentStatusEnum.SUCCEEDED:
                inbox_dto = InboxDTO(
                    event_type=EventTypeEnum.ORDER_PAID,
                    status=InboxEventStatusEnum.PENDING,
                    idempotency_key=payment.idempotency_key,
                    payload=payment.to_dict(),
                )
                outbox_dto = OutboxDTO(
                    event_type=EventTypeEnum.ORDER_PAID,
                    status=OutboxEventStatusEnum.PENDING,
                    payload=NotificationRequest(
                        message="Order is paid",
                        idempotency_key=str(uuid.uuid4())
                    )
                )
                await self.uow.inbox.create(entity=inbox_dto)
                await self.uow.outbox.create(entity=outbox_dto)
                await self.uow.commit()
            if payment.status == PaymentStatusEnum.FAILED:
                inbox_dto = InboxDTO(
                    event_type=EventTypeEnum.ORDER_CANCELLED,
                    status=InboxEventStatusEnum.PENDING,
                    idempotency_key=payment.idempotency_key,
                    payload=payment.to_dict(),
                )
                outbox_dto = OutboxDTO(
                    event_type=EventTypeEnum.ORDER_CANCELLED,
                    status=OutboxEventStatusEnum.PENDING,
                    payload=NotificationRequest(
                        message="Order is cancelled",
                        idempotency_key=str(uuid.uuid4())
                    )
                )
                await self.uow.inbox.create(entity=inbox_dto)
                await self.uow.outbox.create(entity=outbox_dto)
                await self.uow.commit()
