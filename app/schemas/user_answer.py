from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserAnswerCreate(BaseModel):
    is_correct: bool
    question_id: int
    option_id: int
    quiz_attempt_id: int

class UserAnswerUpdate(BaseModel):
    is_correct: Optional[bool] = None
    question_id: Optional[int] = None
    option_id: Optional[int] = None
    quiz_attempt_id: Optional[int] = None

class UserAnswerResponse(BaseModel):
    id: int
    is_correct: bool
    question_id: int
    option_id: int
    quiz_attempt_id: int

    model_config = ConfigDict(from_attributes=True)
