from datetime import datetime
from sqlalchemy import String, DateTime, Double, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Double, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

    options: Mapped[set["Option"]] = relationship(back_populates="question")
    user_answers: Mapped[set["UserAnswer"]] = relationship(back_populates="question")

