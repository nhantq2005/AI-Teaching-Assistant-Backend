from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Sequence, Optional
from app.models.subject import Subject
from app.schemas.subject import SubjectRequest


class SubjectService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        stm = select(Subject).options(selectinload(Subject.lecturer), selectinload(Subject.documents)).where(Subject.id == subject_id)
        result = await self.session.execute(stm)
        return result.scalar_one_or_none()

    async def get_subjects(self, skip: int = 0, limit: int = 100) -> Sequence[Subject]:
        stm = select(Subject).options(selectinload(Subject.lecturer)).offset(skip).limit(limit)
        result = await self.session.execute(stm)
        return result.scalars().all()

    async def create_subject(self, subject: SubjectRequest) -> Subject:
        try:
            db_subject = Subject(**subject.model_dump())
            self.session.add(db_subject)
            await self.session.commit()
            return await self.get_subject_by_id(db_subject.id)
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_subject(self, subject_id: int, subject: SubjectRequest) -> Optional[Subject]:
        try:
            db_subject = await self.get_subject_by_id(subject_id)
            if db_subject:
                update_data = subject.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_subject, key, value)
                await self.session.commit()
                await self.session.refresh(db_subject)
            return db_subject
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_subject(self, subject_id: int) -> bool:
        db_subject = await self.get_subject_by_id(subject_id)
        if db_subject:
            await self.session.delete(db_subject)
            await self.session.commit()
            return True
        return False

    async def get_subjects_by_lecturer(self, lecturer_id: int) -> Sequence[Subject]:
        stm = select(Subject).options(selectinload(Subject.lecturer)).where(Subject.lecturer_id == lecturer_id)
        result = await self.session.execute(stm)
        return result.scalars().all()

