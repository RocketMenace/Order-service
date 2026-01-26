from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.order import OrderStatusDTO

from ..models.order import OrderStatusModel
from .base import BaseRepository


class OrderStatusRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=OrderStatusModel)

    def _model_to_entity(self, model: OrderStatusModel) -> OrderStatusDTO:
        return OrderStatusDTO(
            order_id=str(model.order_id),
        )
