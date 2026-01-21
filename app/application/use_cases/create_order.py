import uuid

from ..interfaces.uow import UnitOfWorkProtocol
from ..dto.order import OrderDTO, OrderStatusDTO, OrderDTOResponse
from ..dto.outbox import OutboxDTO
from ..interfaces.catalog import CatalogServiceProtocol
from ..enums.events import EventTypeEnum, OutboxEventStatusEnum, OrderStatusEnum
from app.core.models.order import Order
from app.core.exceptions.order import ItemNotFoundError, NotEnoughStocksError
from decimal import Decimal
from ..interfaces.contracts import NotificationRequest, PaymentRequest


# TODO Move price calculation logic into Domain model
class CreateOrderUseCase:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        catalog_service: CatalogServiceProtocol,
    ):
        self.uow = uow
        self.catalog_service = catalog_service

    async def __call__(self, order_dto: OrderDTO) -> OrderDTOResponse:
        async with self.uow:
            order = await self.uow.orders.get_order(
                idempotency_key=order_dto.idempotency_key
            )
            if order:
                return order  # Response status code 200 Raise order already exists with data=order
            item = await self.catalog_service.get_item_stock(item_id=order_dto.item_id)
            if not item:
                raise ItemNotFoundError(item_id=order_dto.item_id)
            order = Order(qty=order_dto.quantity, item=item, user_id=order_dto.user_id)

            if not order.can_allocate():
                raise NotEnoughStocksError()

            order_dto.amount = (
                Decimal(order.qty) * order.item.price
            )  # Need move this logic to Domain model

            created_order = await self.uow.orders.create(entity=order_dto)

            order_status_dto = OrderStatusDTO(
                order_id=created_order.id, status=OrderStatusEnum.NEW
            )

            payment_event = OutboxDTO(
                event_type=EventTypeEnum.PAYMENT_REQUESTED,
                payload=PaymentRequest(
                    order_id=str(created_order.id),
                    amount=str(order_dto.amount),
                    idempotency_key=str(order_dto.idempotency_key),
                ),
                status=OutboxEventStatusEnum.PENDING,
            )
            status_event = OutboxDTO(
                event_type=EventTypeEnum.ORDER_CREATED,
                payload=NotificationRequest(
                    message="Order created", idempotency_key=str(uuid.uuid4())
                ),
                status=OutboxEventStatusEnum.PENDING,
            )
            await self.uow.order_status.create(entity=order_status_dto)
            await self.uow.outbox.create(entity=status_event)
            await self.uow.outbox.create(entity=payment_event)

            await self.uow.commit()

            return created_order
