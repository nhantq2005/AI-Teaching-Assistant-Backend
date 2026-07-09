from datetime import datetime
from sqlalchemy import DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class NotificationRead(Base):
    __tablename__ = "notification_read"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="notification_reads")
    notification: Mapped["Notification"] = relationship(back_populates="notification_reads")