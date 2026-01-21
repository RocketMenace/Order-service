from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from ..models.notification import NotificationModel
from app.application.dto.notification import NotificationDTO, NotificationDTOResponse
from sqlalchemy import select, update
from uuid import UUID


class NotificationRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=NotificationModel)

    async def get_notifications(self) -> list[NotificationDTOResponse]:
        query = (
            select(self.model)
            .where(self.model.sent == False)
            .with_for_update(skip_locked=True)
            .limit(100)
        )
        results = (await self.session.execute(query)).scalars().all()
        return [self._model_to_entity(result) for result in results]

    async def mark_as_sent(self, notification_id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == notification_id)
            .values({"sent": True})
        )
        await self.session.execute(query)

    def _model_to_entity(self, model: NotificationModel) -> NotificationDTOResponse:
        return NotificationDTOResponse(
            id=model.id, sent=model.sent, payload=model.payload
        )
