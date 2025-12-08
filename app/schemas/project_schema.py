from datetime import datetime
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name : str = Field(..., min_length=2, max_length=255)
    description: str | None = None

class ProjectUpdate(BaseModel):
    name : str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    workspace_id: int
    created_at: datetime

    class Config:
        from_attributes = True