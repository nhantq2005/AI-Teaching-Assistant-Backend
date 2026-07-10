from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Subject(Base):
    __tablename__ = "subjects"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    lecturer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    lecturer: Mapped["User"] = relationship(back_populates="subjects")

    notifications:Mapped[set["Notification"]] = relationship(back_populates="subject")
    # enrolments: Mapped[set["Enrolment"]] = relationship(back_populates="subject")
    documents: Mapped[set["Document"]] = relationship(back_populates="subject")
    quizzes: Mapped[set["Quiz"]] = relationship(back_populates="subject")