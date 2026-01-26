from enum import StrEnum


class OrderStatusEnum(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
