from enum import StrEnum


class EventTypeEnum(StrEnum):
    ORDER_CREATED = "order.created"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"
    PAYMENT_REQUESTED = "payment.requested"
    SHIPPING_REQUESTED = "shipping.requested"


class OutboxEventStatusEnum(StrEnum):
    PENDING = "pending"
    SENT = "sent"


class InboxEventStatusEnum(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"


class OrderStatusEnum(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class PaymentStatusEnum(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
