# from sqlalchemy import Integer, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
# from models.base import Base
#
#
# class Enrollment(Base):
#     __tablename__ = "enrollments"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     semester: Mapped[int] = mapped_column(Integer, nullable=False)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
#
#     user: Mapped["User"] = mapped_column(relationship(back_populates="enrollments"))