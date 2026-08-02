from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .subject import SubjectResponse

class QuizCreate(BaseModel):
    title: str
    description: str
    time_limit: int
    source_type: str
    difficulty_level: str
    subject_id: Optional[int]

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit: Optional[int] = None
    source_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    subject_id: Optional[int] = None

class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    time_limit: int
    source_type: str
    difficulty_level: str
    created_date: datetime
    updated_date: datetime
    subject_id: int

    model_config = ConfigDict(from_attributes=True)