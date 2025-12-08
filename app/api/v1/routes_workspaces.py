from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceOut, WorkspaceUpdate
from app.models.workspace import Workspace
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)

@router.post("/", response_model=WorkspaceOut, status_code=201)
async def create_workspace(
    data: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if same name exists for SAME user (optional)
    query = select(Workspace).where(
        Workspace.owner_id == current_user.id,
        Workspace.name == data.name
    )

    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Workspace name already exists")

    new_workspace = Workspace(
        name=data.name,
        owner_id=current_user.id
    )

    db.add(new_workspace)
    await db.commit()
    await db.refresh(new_workspace)

    return new_workspace

@router.get("/", response_model=list[WorkspaceOut])
async def get_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Workspace).where(Workspace.owner_id == current_user.id)
    result = await db.execute(query)
    workspaces = result.scalars().all()

    return workspaces

@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(
    workspace_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Workspace).where(
        Workspace.id == workspace_id,
        Workspace.owner_id == current_user.id
    )
    result = await db.execute(query)
    workspace = result.scalar_one_or_none()

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace

@router.put("/{workspace_id}", response_model=WorkspaceOut)
async def update_workspace(
    workspace_id: int,
    data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch workspace
    query = select(Workspace).where(
        Workspace.id == workspace_id,
        Workspace.owner_id == current_user.id
    )
    result = await db.execute(query)
    workspace = result.scalar_one_or_none()

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Update fields
    workspace.name = data.name

    # Save changes
    await db.commit()
    await db.refresh(workspace)

    return workspace

@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch workspace
    query = select(Workspace).where(
        Workspace.id == workspace_id,
        Workspace.owner_id == current_user.id
    )
    result = await db.execute(query)
    workspace = result.scalar_one_or_none()

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Delete workspace
    await db.delete(workspace)
    await db.commit()

    # No return (204 = No Content)
    return None

