from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.workspace import Workspace
from app.models.project import Project
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Projects"])



# Helper: Check workspace owner

async def verify_workspace_owner(workspace_id: int, user_id: int, db: AsyncSession):
    query = select(Workspace).where(Workspace.id == workspace_id)
    result = await db.execute(query)
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if workspace.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return workspace



# CREATE PROJECT
@router.post("/{workspace_id}/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    workspace_id: int,
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await verify_workspace_owner(workspace_id, current_user.id, db)

    new_project = Project(
        name=data.name,
        description=data.description,
        workspace_id=workspace_id,
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return new_project



# GET ALL PROJECTS IN WORKSPACE

@router.get("/{workspace_id}/projects", response_model=list[ProjectResponse])
async def get_projects(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await verify_workspace_owner(workspace_id, current_user.id, db)

    query = select(Project).where(Project.workspace_id == workspace_id)
    result = await db.execute(query)
    return result.scalars().all()


# GET SINGLE PROJECT

@router.get("/{workspace_id}/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    workspace_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await verify_workspace_owner(workspace_id, current_user.id, db)

    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(404, detail="Project not found")

    return project



# UPDATE PROJECT

@router.patch("/{workspace_id}/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    workspace_id: int,
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await verify_workspace_owner(workspace_id, current_user.id, db)

    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(404, detail="Project not found")

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description

    await db.commit()
    await db.refresh(project)

    return project


# DELETE PROJECT
@router.delete("/{workspace_id}/projects/{project_id}", status_code=204)
async def delete_project(
    workspace_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await verify_workspace_owner(workspace_id, current_user.id, db)

    query = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(404, detail="Project not found")

    await db.delete(project)
    await db.commit()

    return None
