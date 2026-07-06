import uuid

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"
    id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_attempt_id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True))
    selected_option_id: Mapped[uuid.UUID] = mapped_column(uuid.UUID(as_uuid=True))

    attemp:Mapped[str] = mapped_column(relationship("QuizAttempt", back_populates="user_answers"))