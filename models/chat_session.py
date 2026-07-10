import uuid
from datetime import datetime

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    created_date: Mapped[datetime] = mapped_column(nullable=False)
    updated_date: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_sessions")

    chat_messages: Mapped[set["ChatMessage"]] = relationship(back_populates="chat_session")