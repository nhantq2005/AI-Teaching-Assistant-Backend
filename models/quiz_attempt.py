import uuid
from datetime import datetime

from sqlalchemy import Double, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True), nullable=False)
    total_score: Mapped[float] = mapped_column(Double, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    time_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    quiz:Mapped[str] = mapped_column(relationship("Quiz", back_populates="quiz_attempts"))
    user_answers: Mapped[str] = mapped_column(relationship("UserAnswer", back_populates="quiz_attempt"))