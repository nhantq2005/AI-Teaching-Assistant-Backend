from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

def get_enrollment_service(session: AsyncSession = Depends(get_db)):
    return EnrollmentService(session)

@router.post("/", response_model=EnrollmentResponse)
async def create_enrollment(enrollment: EnrollmentCreate, enrollment_service: EnrollmentService = Depends(get_enrollment_service)):
    return await enrollment_service.create_enrollment(enrollment=enrollment)

@router.get("/", response_model=List[EnrollmentResponse])
async def read_enrollments(skip: int = 0, limit: int = 100, enrollment_service: EnrollmentService = Depends(get_enrollment_service)):
    return await enrollment_service.get_enrollments(skip=skip, limit=limit)

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def read_enrollment(enrollment_id: int, enrollment_service: EnrollmentService = Depends(get_enrollment_service)):
    db_enrollment = await enrollment_service.get_enrollment(enrollment_id=enrollment_id)
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return db_enrollment

@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(enrollment_id: int, enrollment: EnrollmentUpdate, enrollment_service: EnrollmentService = Depends(get_enrollment_service)):
    db_enrollment = await enrollment_service.update_enrollment(enrollment_id=enrollment_id, enrollment=enrollment)
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return db_enrollment

@router.delete("/{enrollment_id}")
async def delete_enrollment(enrollment_id: int, enrollment_service: EnrollmentService = Depends(get_enrollment_service)):
    success = await enrollment_service.delete_enrollment(enrollment_id=enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"message": "Enrollment deleted successfully"}
