from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.question import Question
from app.models.option import Option
from app.schemas.question import QuestionRequest
from sqlalchemy.orm import selectinload

class QuestionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        result = await self.session.execute(select(Question).options(selectinload(Question.options)).where(Question.id == question_id))
        return result.scalars().first()

    async def get_questions(self, params: dict) -> List[Question]:
        skip = params.get("skip", 0)
        limit = params.get("limit", 100)
        result = await self.session.execute(select(Question).options(selectinload(Question.options)).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create_question(self, question_request: QuestionRequest) -> Question:
        question_data = question_request.model_dump(exclude={"options"})
        db_question = Question(**question_data)
        self.session.add(db_question)
        await self.session.flush()

        for opt in question_request.options:
            opt_data = opt.model_dump(exclude={"question_id"})
            db_option = Option(**opt_data, question_id=db_question.id)
            self.session.add(db_option)

        await self.session.commit()
        result = await self.session.execute(
            select(Question).options(selectinload(Question.options)).where(Question.id == db_question.id)
        )
        return result.scalars().first()


    async def get_question_by_quiz(self, quiz_id: int) -> List[Question]:
        result = await self.session.execute(select(Question).options(selectinload(Question.options)).where(Question.quiz_id == quiz_id))
        return list(result.scalars().all())

    async def update_question(self, question_id: int, question_request: QuestionRequest) -> Optional[Question]:
        db_question = await self.get_question_by_id(question_id)
        if db_question:
            update_data = question_request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key != "options": # Don't update options this way
                    setattr(db_question, key, value)
            await self.session.commit()
            await self.session.refresh(db_question)
            
            # Re-fetch to eager load options after refresh
            result = await self.session.execute(select(Question).options(selectinload(Question.options)).where(Question.id == question_id))
            return result.scalars().first()
        return db_question

    async def delete_question(self, question_id: int) -> bool:
        db_question = await self.get_question_by_id(question_id)
        if db_question:
            await self.session.delete(db_question)
            await self.session.commit()
            return True
        return False