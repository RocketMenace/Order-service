from sqlalchemy import JSON, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column

from ..models.base import BaseModel
from sqlalchemy.dialects.postgresql import JSONB


class NotificationModel(BaseModel):
    __tablename__ = "notifications"
    payload: Mapped[JSONB] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    sent: Mapped[bool] = mapped_column(BOOLEAN, default=False)
