from typing import Optional
from pydantic import BaseModel, ConfigDict

class OptionRequest(BaseModel):
    content: str
    is_correct: bool = False
    question_id: Optional[int] = None

class OptionResponse(BaseModel):
    id: int
    content: str
    is_correct: bool
    question_id: int

    model_config = ConfigDict(from_attributes=True)