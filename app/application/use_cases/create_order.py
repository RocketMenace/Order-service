import uuid

from app.application.dto import (OrderDTO, OrderDTOResponse, OrderStatusDTO,
                                 OutboxDTO)
from app.application.enums.events import (EventTypeEnum, OrderStatusEnum,
                                          OutboxEventStatusEnum)
from app.application.interfaces import (CatalogServiceProtocol,
                                        NotificationRequest, PaymentRequest,
                                        UnitOfWorkProtocol)
from app.core.exceptions import (ItemNotFoundError, NotEnoughStocksError,
                                 OrderAlreadyExistsError, OrderResponseData)
from app.core.models.order import Order


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
                raise OrderAlreadyExistsError(data=OrderResponseData(**order.to_dict()))
            item = await self.catalog_service.get_item_stock(item_id=order_dto.item_id)
            if not item:
                raise ItemNotFoundError(item_id=order_dto.item_id)
            order = Order(qty=order_dto.quantity, item=item, user_id=order_dto.user_id)

            if not order.can_allocate():
                raise NotEnoughStocksError()

            order_dto.amount = order.calculate_amount(price=item.price)

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
