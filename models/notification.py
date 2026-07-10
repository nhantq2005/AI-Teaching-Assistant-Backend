from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=True)

    subject: Mapped["Subject"] = relationship(back_populates="notifications")

    notification_reads: Mapped[set["NotificationRead"]] = relationship(back_populates="notification")

