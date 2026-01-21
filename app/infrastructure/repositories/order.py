from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from ..models.order import OrderModel
from uuid import UUID
from app.application.dto.order import OrderDTOResponse


class OrderRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=OrderModel)

    async def get_order(self, idempotency_key: UUID) -> OrderDTOResponse | None:
        query = select(self.model).where(self.model.idempotency_key == idempotency_key)
        result = (await self.session.execute(query)).scalar_one_or_none()
        if not result:
            return None
        return self._model_to_entity(result)

    def _model_to_entity(self, model: OrderModel) -> OrderDTOResponse:
        return OrderDTOResponse(
            id=model.id,
            user_id=model.user_id,
            idempotency_key=str(model.idempotency_key),
            amount=model.amount,
            quantity=model.quantity,
            item_id=str(model.item_id),
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat(),
        )
