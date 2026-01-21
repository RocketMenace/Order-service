from ..interfaces.uow import UnitOfWorkProtocol
from ..interfaces.notifications import NotificationsServiceProtocol
from ..enums.events import OutboxEventStatusEnum, EventTypeEnum
from ..interfaces.contracts import NotificationRequest


class SendNotificationUseCase:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        notification_service: NotificationsServiceProtocol,
    ):
        self.uow = uow
        self.notifications_service = notification_service

    async def __call__(self) -> None:
        async with self.uow:
            notifications = await self.uow.outbox.get_events(
                event_type=EventTypeEnum.ORDER_CREATED,
                status=OutboxEventStatusEnum.PENDING,
            )
            if not notifications:
                return None
            for notification in notifications:
                if await self.notifications_service.send_notification(
                    payload=NotificationRequest(
                        message=notification.payload.get("message"),
                        idempotency_key=notification.payload.get("idempotency_key"),
                    )
                ):
                    await self.uow.outbox.mark_as_sent(notification.id)
                    await self.uow.commit()
            return None
