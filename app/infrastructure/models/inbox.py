from .base import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, JSON, Index, CheckConstraint, UUID as SQLUUID
from .enums import EventTypeEnum, InboxEventStatusEnum
from uuid import UUID


class InboxModel(BaseModel):
    __tablename__ = "inbox"
    __table_args__ = (
        Index("idx_status_inbox", "status"),
        CheckConstraint("status IN ('pending', 'sent')", name="valid_outbox_status"),
    )
    event_type: Mapped[EventTypeEnum] = mapped_column(
        Enum(EventTypeEnum, name="eventtypeenum", values_callable=lambda obj: [e.value for e in obj]), 
        default=EventTypeEnum.ORDER_CREATED
    )
    payload: Mapped[JSONB] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    status: Mapped[InboxEventStatusEnum] = mapped_column(
        Enum(InboxEventStatusEnum, name="inboxeventstatusenum", values_callable=lambda obj: [e.value for e in obj]), 
        default=InboxEventStatusEnum.PENDING
    )
    idempotency_key: Mapped[UUID] = mapped_column(SQLUUID, unique=True)
