from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Enum as SqlEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    LECTURER = "LECTURER"
    STUDENT = "STUDENT"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    documents: Mapped[set["Document"]] = relationship(back_populates="lecturer")
    attempt_quizzes: Mapped[set["AttemptQuiz"]] = relationship(back_populates="user")
    subjects: Mapped[set["Subject"]] = relationship(back_populates="lecturer")
    # enrollments: Mapped[set["Enrollment"]] = relationship(back_populates="user")
    notification_reads: Mapped[set["NotificationRead"]] = relationship(back_populates="user")
    chat_sessions: Mapped[set["ChatSession"]] = relationship(back_populates="user")
