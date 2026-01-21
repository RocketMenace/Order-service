import asyncio
from app.application.use_cases.create_payment import CreatePaymentUseCase
from app.application.use_cases.send_notification import SendNotificationUseCase
from app.infrastructure.config.database import Database
from app.infrastructure.uow import UnitOfWork
from app.infrastructure.adapters.payments import PaymentsService
from app.infrastructure.adapters.notifications import NotificationsService


class OutboxPaymentsWorker:
    def __init__(
        self,
        database: Database,
        payments_service: PaymentsService,
    ):
        self.database = database
        self.payments_service = payments_service

    async def run(self):
        while True:
            session = self.database.create_session()
            try:
                uow = UnitOfWork(session=session)
                use_case = CreatePaymentUseCase(
                    uow=uow, payments_service=self.payments_service
                )
                await use_case()
            except Exception:
                if not session.close:
                    await session.rollback()
                    await session.close()
                raise
            await asyncio.sleep(5)


class OutboxNotificationsWorker:
    def __init__(
        self,
        database: Database,
        notifications_service: NotificationsService,
    ):
        self.database = database
        self.notifications_service = notifications_service

    async def run(self):
        while True:
            session = self.database.create_session()
            try:
                uow = UnitOfWork(session=session)
                use_case = SendNotificationUseCase(
                    uow=uow, notification_service=self.notifications_service
                )
                await use_case()
            except Exception:
                if not session.close:
                    await session.rollback()
                    await session.close()
                raise
            await asyncio.sleep(5)
