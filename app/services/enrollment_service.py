from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate

class EnrollmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_enrollment(self, enrollment_id: int) -> Optional[Enrollment]:
        result = await self.session.execute(select(Enrollment).where(Enrollment.id == enrollment_id))
        return result.scalars().first()

    async def get_enrollments(self, skip: int = 0, limit: int = 100) -> Sequence[Enrollment]:
        result = await self.session.execute(select(Enrollment).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_enrollment(self, enrollment: EnrollmentCreate) -> Enrollment:
        db_enrollment = Enrollment(**enrollment.model_dump())
        self.session.add(db_enrollment)
        await self.session.commit()
        await self.session.refresh(db_enrollment)
        return db_enrollment

    async def update_enrollment(self, enrollment_id: int, enrollment: EnrollmentUpdate) -> Optional[Enrollment]:
        db_enrollment = await self.get_enrollment(enrollment_id)
        if db_enrollment:
            update_data = enrollment.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_enrollment, key, value)
            await self.session.commit()
            await self.session.refresh(db_enrollment)
        return db_enrollment

    async def delete_enrollment(self, enrollment_id: int) -> bool:
        db_enrollment = await self.get_enrollment(enrollment_id)
        if db_enrollment:
            await self.session.delete(db_enrollment)
            await self.session.commit()
            return True
        return False

    async def get_enrollments_by_user(self, user_id: int) -> Sequence[Enrollment]:
        result = await self.session.execute(select(Enrollment).where(Enrollment.user_id == user_id))
        return result.scalars().all()
    
    async def get_enrollments_by_subject(self, subject_id: int) -> Sequence[Enrollment]:
        result = await self.session.execute(select(Enrollment).where(Enrollment.subject_id == subject_id))
        return result.scalars().all()
