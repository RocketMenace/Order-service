from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from .base import BaseRepository
from ..models.inbox import InboxModel
from app.application.dto.inbox import InboxDTOResponse, InboxDTO
from uuid import UUID

from ...application.enums.events import (
    EventTypeEnum,
    InboxEventStatusEnum,
)


class InboxRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=InboxModel)

    async def create(self, entity: InboxDTO) -> None:
        query = (
            insert(self.model)
            .values(**entity.to_dict())
            .on_conflict_do_nothing(index_elements=["idempotency_key"])
        )
        await self.session.execute(query)

    async def get_events(
        self,
        event_type: EventTypeEnum | None = None,
        status: InboxEventStatusEnum | None = None,
        limit: int | None = 100,
    ):
        query = select(self.model)

        conditions = []
        if event_type is not None:
            conditions.append(self.model.event_type == event_type)
        if status is not None:
            conditions.append(self.model.status == status)

        if conditions:
            query = query.where(*conditions)

        query = query.with_for_update(skip_locked=True)

        if limit is not None:
            query = query.limit(limit)

        results = (await self.session.execute(query)).scalars().all()
        return [self._model_to_entity(result) for result in results]

    async def get_event(self, idempotency_key: UUID) -> InboxDTOResponse | None:
        query = select(self.model).where(self.model.idempotency_key == idempotency_key)
        result = (await self.session.execute(query)).scalar_one_or_none()
        if not result:
            return None
        return self._model_to_entity(result)

    async def mark_as_processed(self, event_id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == event_id)
            .values(status=InboxEventStatusEnum.PROCESSED)
        )
        await self.session.execute(query)

    def _model_to_entity(self, model: InboxModel) -> InboxDTOResponse:
        return InboxDTOResponse(
            id=model.id,
            event_type=model.event_type,
            status=model.status,
            payload=model.payload,
            idempotency_key=model.idempotency_key,
        )
