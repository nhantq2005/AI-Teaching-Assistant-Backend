from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.schemas.question import QuestionRequest, QuestionResponse
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

def get_question_service(db: AsyncSession = Depends(get_db)):
    return QuestionService(session=db)

@router.post("/", response_model=QuestionResponse)
async def create_question(question: QuestionRequest, service: QuestionService = Depends(get_question_service)):
    return await service.create_question(question_request=question)

@router.get("/quiz/{quiz_id}", response_model=List[QuestionResponse])
async def get_questions_by_quiz(quiz_id: int, service: QuestionService = Depends(get_question_service)):
    return await service.get_question_by_quiz(quiz_id=quiz_id)  

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(params:dict, service: QuestionService = Depends(get_question_service)):
    return await service.get_questions(params=params)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question_by_id(question_id: int, service: QuestionService = Depends(get_question_service)):
    db_question = await service.get_question_by_id(question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionRequest, service: QuestionService = Depends(get_question_service)):
    db_question = await service.update_question(question_id=question_id, question_request=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.delete("/{question_id}")
async def delete_question(question_id: int, service: QuestionService = Depends(get_question_service)):
    success = await service.delete_question(question_id=question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}
