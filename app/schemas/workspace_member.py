from pydantic import BaseModel, EmailStr
from datetime import datetime


class WorkspaceMemberBase(BaseModel):
    role: str = "member"   # default role


class WorkspaceMemberCreate(BaseModel):
    email: EmailStr        # we will add by email
    role: str = "member"   # admin/member


class WorkspaceMemberResponse(BaseModel):
    id: int
    user_id: int
    workspace_id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceMemberUserInfo(BaseModel):
    """Useful for listing members with their user info"""
    id: int
    email: EmailStr
    full_name: str | None = None

    class Config:
        from_attributes = True


class WorkspaceMemberListResponse(BaseModel):
    member_id: int
    role: str
    user: WorkspaceMemberUserInfo
