from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.session import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

from app.schemas.workspace_member import (
    WorkspaceMemberCreate,
    WorkspaceMemberResponse,
    WorkspaceMemberListResponse,
    WorkspaceMemberUserInfo
)

from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspace Members"])


# -------------------------------------
# Helper: Check Workspace Ownership
# -------------------------------------
async def require_owner_or_admin(workspace_id: int, user_id: int, db: AsyncSession):
    # Check workspace owner
    ws = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = ws.scalar_one_or_none()

    if not workspace:
        raise HTTPException(404, "Workspace not found")

    # If owner -> allowed
    if workspace.owner_id == user_id:
        return workspace

    # Otherwise check if user is admin member
    q = await db.execute(
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .where(WorkspaceMember.user_id == user_id)
    )
    member = q.scalar_one_or_none()

    if not member or member.role != "admin":
        raise HTTPException(403, "You are not allowed")

    return workspace


# ----------------------------------------------------------------
# 1️⃣ ADD MEMBER TO WORKSPACE
# ----------------------------------------------------------------
@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
async def add_member(
    workspace_id: int,
    payload: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # Check permission
    await require_owner_or_admin(workspace_id, current_user.id, db)

    # Find user by email
    u = await db.execute(select(User).where(User.email == payload.email))
    user = u.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    # Check already member
    ex = await db.execute(
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .where(WorkspaceMember.user_id == user.id)
    )
    exists = ex.scalar_one_or_none()

    if exists:
        raise HTTPException(400, "User already a member")

    # Add workspace member
    member = WorkspaceMember(
        user_id=user.id,
        workspace_id=workspace_id,
        role=payload.role,
    )

    db.add(member)
    await db.commit()
    await db.refresh(member)

    return member


# ----------------------------------------------------------------
# 2️⃣ LIST MEMBERS
# ----------------------------------------------------------------
@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberListResponse])
async def list_members(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # Permission check
    await require_owner_or_admin(workspace_id, current_user.id, db)

    # Fetch members + join user table
    result = await db.execute(
        select(
            WorkspaceMember.id,
            WorkspaceMember.role,
            User.id,
            User.email,
            User.full_name
        )
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )

    rows = result.all()

    # Transform into schema
    output = []
    for member_id, role, user_id, email, full_name in rows:
        output.append(
            WorkspaceMemberListResponse(
                member_id=member_id,
                role=role,
                user=WorkspaceMemberUserInfo(
                    id=user_id,
                    email=email,
                    full_name=full_name
                )
            )
        )

    return output


# ----------------------------------------------------------------
# 3️⃣ REMOVE MEMBER
# ----------------------------------------------------------------
@router.delete("/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # Permission check
    await require_owner_or_admin(workspace_id, current_user.id, db)

    # Avoid removing yourself
    if user_id == current_user.id:
        raise HTTPException(400, "You cannot remove yourself")

    # Delete member
    q = await db.execute(
        delete(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .where(WorkspaceMember.user_id == user_id)
        .returning(WorkspaceMember.id)
    )

    deleted = q.scalar_one_or_none()

    if not deleted:
        raise HTTPException(404, "Member not found")

    await db.commit()
    return {"message": "Member removed successfully"}
