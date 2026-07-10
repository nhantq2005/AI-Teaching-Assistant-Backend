import uuid

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    chat_session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)

    chat_session: Mapped["ChatSession"] = relationship(back_populates="chat_messages")

    chat_citations: Mapped[set["ChatCitation"]] = relationship(back_populates="chat_message")