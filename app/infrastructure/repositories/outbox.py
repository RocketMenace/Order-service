from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert

from .base import BaseRepository
from ..models.outbox import OutboxModel
from ..models.enums import EventTypeEnum, OutboxEventStatusEnum
from app.application.dto.outbox import OutboxDTO, OutboxDTOResponse


class OutboxRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=OutboxModel)

    async def create(self, entity: OutboxDTO) -> None:
        query = insert(self.model).values(**entity.to_dict())
        await self.session.execute(query)

    async def get_events(
        self,
        event_type: EventTypeEnum | None = None,
        status: OutboxEventStatusEnum | None = None,
        limit: int | None = 100,
    ) -> list[OutboxDTOResponse] | list[None]:
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

    async def get_unsent_notifications(self) -> list[OutboxDTOResponse] | list[None]:
        query = select(self.model).where(
            self.model.status == OutboxEventStatusEnum.PENDING,
            self.model.event_type.in_(
                [
                    EventTypeEnum.ORDER_CREATED,
                    EventTypeEnum.ORDER_PAID,
                    EventTypeEnum.ORDER_CANCELLED,
                    EventTypeEnum.ORDER_SHIPPED,
                ]
            ),
        )
        query = query.with_for_update(skip_locked=True)
        results = (await self.session.execute(query)).scalars().all()
        return [self._model_to_entity(result) for result in results]

    async def mark_as_sent(self, event_id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == event_id)
            .values(status=OutboxEventStatusEnum.SENT)
        )
        await self.session.execute(query)

    def _model_to_entity(self, model: OutboxModel) -> OutboxDTOResponse:
        return OutboxDTOResponse(
            id=model.id,
            event_type=model.event_type,
            payload=model.payload,
            status=model.status,
        )
