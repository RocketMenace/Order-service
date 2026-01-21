from sqlalchemy.orm import relationship

from .base import BaseModel, Mapped, mapped_column
from decimal import Decimal
from sqlalchemy import (
    Numeric,
    String,
    Index,
    Integer,
    CheckConstraint,
    UUID as SQLUUID,
    ForeignKey,
    Enum,
)
from uuid import UUID
from .enums import OrderStatusEnum


class OrderModel(BaseModel):
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_item_id", "item_id"),
        CheckConstraint("amount >= 0", name="positive_amount"),
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
    )
    user_id: Mapped[str] = mapped_column(String(255))
    item_id: Mapped[UUID] = mapped_column(SQLUUID)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=19, scale=2), default=Decimal("0.00")
    )
    idempotency_key: Mapped[UUID] = mapped_column(SQLUUID, unique=True)

    # === RELATIONSHIPS ===
    order_status_history: Mapped[list["OrderStatusModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderStatusModel.created_at.desc()",
    )


class OrderStatusModel(BaseModel):
    __tablename__ = "order_status"
    __table_args__ = (
        Index("idx_order_id", "order_id"),
        Index("idx_order_id_status", "order_id", "status"),
        CheckConstraint(
            "status IN ('new', 'paid', 'shipped', 'cancelled')",
            name="valid_order_status",
        ),
    )
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey(column="orders.id", ondelete="CASCADE")
    )
    status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(OrderStatusEnum), default=OrderStatusEnum.NEW
    )

    # === RELATIONSHIPS ===
    order: Mapped[OrderModel] = relationship(back_populates="order_status_history")
