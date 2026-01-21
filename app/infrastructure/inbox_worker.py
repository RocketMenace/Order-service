import asyncio
from app.application.use_cases.update_status import UpdateOrderStatusUseCase
from app.infrastructure.config.database import Database
from app.infrastructure.uow import UnitOfWork


class InboxWorker:
    def __init__(
        self,
        database: Database,
    ):
        self.database = database

    async def run(self):
        while True:
            session = self.database.create_session()
            try:
                uow = UnitOfWork(session=session)
                use_case = UpdateOrderStatusUseCase(uow=uow)
                await use_case()
            except Exception:
                if not session.close:
                    await session.rollback()
                    await session.close()
                raise
            await asyncio.sleep(5)
