from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse


class SubjectRequest(BaseModel):
    name: str
    code: str
    description: str
    lecturer_id: int

class SubjectResponse(SubjectRequest):
    id: int
    name: str
    code: str
    description: str
    created_date: datetime
    lecturer: UserResponse

    model_config = ConfigDict(from_attributes=True)
