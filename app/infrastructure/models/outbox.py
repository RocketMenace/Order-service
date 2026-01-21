from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, JSON, Index, CheckConstraint

from .base import BaseModel
from .enums import EventTypeEnum, OutboxEventStatusEnum


class OutboxModel(BaseModel):
    __tablename__ = "outbox"
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_event_type_status_type", "event_type", "status"),
        CheckConstraint("status IN ('pending', 'sent')", name="valid_outbox_status"),
    )
    event_type: Mapped[EventTypeEnum] = mapped_column(
        Enum(EventTypeEnum), default=EventTypeEnum.ORDER_CREATED
    )
    payload: Mapped[JSONB] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    status: Mapped[OutboxEventStatusEnum] = mapped_column(
        Enum(OutboxEventStatusEnum), default=OutboxEventStatusEnum.PENDING
    )
