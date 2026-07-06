import uuid

from sqlalchemy import UUID, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.question import Question


class Option(Base):
    __tablename__ = "option"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable =False)

    question: Mapped[Question] = mapped_column(relationship("Question", back_populates="options"))

