from pydantic import BaseModel
from datetime import datetime

class ActivityLogBase(BaseModel):
    action: str
    old_value: str | None = None
    new_value: str | None = None

class ActivityLogCreate(ActivityLogBase):
    user_id: int
    task_id: int | None = None

class ActivityLogResponse(BaseModel):
    id: int
    action: str
    old_value: str | None
    new_value: str | None
    user_id: int
    task_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
