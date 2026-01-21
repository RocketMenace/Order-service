from enum import StrEnum


class OrderStatusEnum(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class EventTypeEnum(StrEnum):
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_SHIPPED = "order.shipped"
    PAYMENT_REQUESTED = "payment.requested"
    SHIPPING_REQUESTED = "shipping.requested"


class OutboxEventStatusEnum(StrEnum):
    PENDING = "pending"
    SENT = "sent"


class InboxEventStatusEnum(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
