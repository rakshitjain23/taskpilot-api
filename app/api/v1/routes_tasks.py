from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.utils.dependencies import get_current_user

from app.models.workspace import Workspace
from app.models.project import Project
from app.models.task import Task

from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

router = APIRouter(prefix="/workspaces", tags=["Tasks"])

# Helper: Check workspace owner

async def verify_workspace_owner(workspace_id: int, user_id: int, db: AsyncSession):
    q = select(Workspace).where(Workspace.id == workspace_id)
    res = await db.execute(q)
    ws = res.scalar_one_or_none()

    if not ws:
        raise HTTPException(404, "Workspace not found")

    if ws.owner_id != user_id:
        raise HTTPException(403, "Not allowed")

    return ws

# Helper: Check project in workspace
async def get_project_or_404(project_id: int, workspace_id: int, db: AsyncSession):
    q = select(Project).where(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    )
    res = await db.execute(q)
    project = res.scalar_one_or_none()

    if not project:
        raise HTTPException(404, "Project not found")

    return project

# CREATE TASK

@router.post("/{workspace_id}/projects/{project_id}/tasks",
             response_model=TaskResponse, status_code=201)
async def create_task(
    workspace_id: int,
    project_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # verify user owns workspace
    await verify_workspace_owner(workspace_id, current_user.id, db)

    # ensure project belongs to same workspace
    await get_project_or_404(project_id, workspace_id, db)

    new_task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        assignee_id=data.assignee_id,
        project_id=project_id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task

# GET ALL TASKS OF A PROJECT

@router.get("/{workspace_id}/projects/{project_id}/tasks",
            response_model=list[TaskResponse])
async def get_tasks(
    workspace_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    await verify_workspace_owner(workspace_id, current_user.id, db)
    await get_project_or_404(project_id, workspace_id, db)

    q = select(Task).where(Task.project_id == project_id)
    res = await db.execute(q)
    return res.scalars().all()

# GET SINGLE TASK
@router.get("/{workspace_id}/projects/{project_id}/tasks/{task_id}",
            response_model=TaskResponse)
async def get_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    await verify_workspace_owner(workspace_id, current_user.id, db)
    await get_project_or_404(project_id, workspace_id, db)

    q = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    res = await db.execute(q)
    task = res.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    return task

# UPDATE TASK
@router.patch("/{workspace_id}/projects/{project_id}/tasks/{task_id}",
              response_model=TaskResponse)
async def update_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    await verify_workspace_owner(workspace_id, current_user.id, db)
    await get_project_or_404(project_id, workspace_id, db)

    q = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    res = await db.execute(q)
    task = res.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
    if data.assignee_id is not None:
        task.assignee_id = data.assignee_id

    await db.commit()
    await db.refresh(task)

    return task



# DELETE TASK
@router.delete("/{workspace_id}/projects/{project_id}/tasks/{task_id}",
               status_code=204)
async def delete_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await verify_workspace_owner(workspace_id, current_user.id, db)
    await get_project_or_404(project_id, workspace_id, db)

    q = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    res = await db.execute(q)
    task = res.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    await db.delete(task)
    await db.commit()

    return None
