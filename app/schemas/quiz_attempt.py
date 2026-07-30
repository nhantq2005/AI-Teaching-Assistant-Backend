from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class QuizAttemptCreate(BaseModel):
    total_score: float
    is_completed: bool = False
    total_questions: int
    correct_count: int
    time_start: Optional[datetime] = None
    time_submitted: Optional[datetime] = None
    user_id: int
    quiz_id: int

class QuizAttemptUpdate(BaseModel):
    total_score: Optional[float] = None
    is_completed: Optional[bool] = None
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    time_start: Optional[datetime] = None
    time_submitted: Optional[datetime] = None

class QuizAttemptResponse(BaseModel):
    id: int
    total_score: float
    is_completed: bool
    total_questions: int
    correct_count: int
    time_start: Optional[datetime] = None
    time_submitted: Optional[datetime] = None
    created_date: datetime
    user_id: int
    quiz_id: int

    model_config = ConfigDict(from_attributes=True)
