from typing import Optional
from pydantic import BaseModel, ConfigDict

class QuizAnswerCreate(BaseModel):
    is_correct: bool = False

class QuizAnswerUpdate(BaseModel):
    is_correct: Optional[bool] = None

class QuizAnswerResponse(BaseModel):
    id: int
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)
