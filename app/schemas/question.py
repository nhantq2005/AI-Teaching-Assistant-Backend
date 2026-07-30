from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List
from app.schemas.option import OptionResponse, OptionRequest


class QuestionRequest(BaseModel):
    question: str
    score : float
    quiz_id: int
    options: List[OptionRequest]

class QuestionResponse(BaseModel):
    id: int
    question: str
    score : float
    created_date: datetime
    quiz_id: int
    options: List[OptionResponse]

    model_config = ConfigDict(from_attributes=True)