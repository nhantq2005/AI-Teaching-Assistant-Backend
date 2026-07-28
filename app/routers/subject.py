from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.subject import SubjectRequest, SubjectResponse
from app.services.subject_service import SubjectService
from app.db.session import get_db

router = APIRouter(prefix="/subjects", tags=["Subjects"])


def get_subject_service(session: AsyncSession = Depends(get_db)):
    return SubjectService(session)


@router.post("/", response_model=SubjectResponse)
async def create_subject(subject: SubjectRequest, subject_service: SubjectService = Depends(get_subject_service)):
    return await subject_service.create_subject(subject=subject)


@router.get("/", response_model=List[SubjectResponse])
async def read_subjects(skip: int = 0, limit: int = 100,
                        subject_service: SubjectService = Depends(get_subject_service)):
    return await subject_service.get_subjects(skip=skip, limit=limit)


@router.get("/{subject_id}", response_model=SubjectResponse)
async def read_subject(subject_id: int, subject_service: SubjectService = Depends(get_subject_service)):
    db_subject = await subject_service.get_subject_by_id(subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: int, subject: SubjectRequest,
                         subject_service: SubjectService = Depends(get_subject_service)):
    db_subject = await subject_service.update_subject(subject_id=subject_id, subject=subject)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
        subject_id: int,
        subject_service: SubjectService = Depends(get_subject_service)
):
    success = await subject_service.delete_subject(subject_id=subject_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return None
