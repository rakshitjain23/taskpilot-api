from datetime import datetime
from pydantic import BaseModel, Field
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    assignee_id: int | None = None 
    status: TaskStatus = TaskStatus.TODO

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    assignee_id: int | None
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True