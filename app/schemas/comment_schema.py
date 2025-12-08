from pydantic import BaseModel
from datetime import datetime

# Base Schema
class CommentBase(BaseModel):
    content: str

# Create Schema
class CommentCreate(CommentBase):
    pass

# Update Schema
class CommentUpdate(BaseModel):
    content: str

# Response Schema
class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
