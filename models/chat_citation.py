from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ChatCitation(Base):
    __tablename__ = "chat_citations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    similarity_score: Mapped[float] = mapped_column(nullable=False)
    document_chunk_id: Mapped[int] = mapped_column(ForeignKey("document_chunks.id"), nullable=False)
    chat_message_id: Mapped[int] = mapped_column(ForeignKey("chat_messages.id"), nullable=False)

    document_chunk: Mapped["DocumentChunk"] = mapped_column(relationship(back_populates="chat_citations"))
    chat_message: Mapped["ChatMessage"] = mapped_column(relationship(back_populates="chat_citations"))
