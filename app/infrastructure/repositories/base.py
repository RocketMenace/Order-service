from typing import Generic
from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.type_vars import TEntity, TModel


class BaseRepository(Generic[TEntity, TModel]):
    def __init__(
        self,
        session: AsyncSession,
        model: type[TModel],
    ):
        self.session = session
        self.model = model

    async def create(self, entity: TEntity) -> TEntity:
        query = insert(self.model).values(**entity.to_dict()).returning(self.model)
        result = (await self.session.execute(query)).scalar_one()
        return self._model_to_entity(result)

    async def get_by_id(self, entity_id: UUID) -> TEntity | None:
        query = select(self.model).where(self.model.id == entity_id)
        result = (await self.session.execute(query)).scalar_one_or_none()
        if not result:
            return None
        return self._model_to_entity(result)

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        model_instance = result.scalar_one_or_none()
        if model_instance is None:
            return False

        await self.session.delete(model_instance)
        await self.session.flush()
        return True

    def _model_to_entity(self, model: TModel) -> TEntity:
        raise NotImplementedError("Subclasses must implement _model_to_entity method")
