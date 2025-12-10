from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, desc

from app.db.session import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)
from app.schemas.activity_log_schema import ActivityLogResponse
from app.models.activity_log import ActivityLog
from app.models.task import Task, TaskStatus
from app.models.project import Project
from app.utils.activity_logger import create_activity_log

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=TaskResponse)
async def create_task(
    project_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check if project exists
    q = await db.execute(select(Project).where(Project.id == project_id))
    project = q.scalar_one_or_none()

    if not project:
        raise HTTPException(404, "Project not found")

    # Create task
    stmt = (
        insert(Task)
        .values(
            title=data.title,
            description=data.description,
            status=TaskStatus.TODO,
            project_id=project_id,
        )
        .returning(Task)
    )
    result = await db.execute(stmt)
    await db.commit()

    task = result.scalar_one()

    # Log: TASK CREATED
    await create_activity_log(
        db,
        user_id=current_user.id,
        task_id=task.id,
        action="TASK_CREATED",
        new_value=task.title
    )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch existing task
    q = await db.execute(select(Task).where(Task.id == task_id))
    task = q.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    # Save old values for logs
    old = {
        "title": task.title,
        "description": task.description,
    }

    # Apply changes
    upd = (
        update(Task)
        .where(Task.id == task_id)
        .values(
            title=data.title or task.title,
            description=data.description or task.description,
        )
        .returning(Task)
    )

    result = await db.execute(upd)
    await db.commit()

    updated_task = result.scalar_one()

    # Log: TASK_UPDATED
    await create_activity_log(
        db,
        user_id=current_user.id,
        task_id=task_id,
        action="TASK_UPDATED",
        old_value=str(old),
        new_value=str(
            {"title": updated_task.title, "description": updated_task.description}
        )
    )

    return updated_task


@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status: TaskStatus,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = await db.execute(select(Task).where(Task.id == task_id))
    task = q.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    old_status = task.status.value

    upd = (
        update(Task)
        .where(Task.id == task_id)
        .values(status=status)
        .returning(Task)
    )

    result = await db.execute(upd)
    await db.commit()

    updated = result.scalar_one()

    # Log: STATUS_CHANGED
    await create_activity_log(
        db,
        user_id=current_user.id,
        task_id=task_id,
        action="STATUS_CHANGED",
        old_value=old_status,
        new_value=status.value
    )

    return updated

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = await db.execute(select(Task).where(Task.id == task_id))
    task = q.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    del_stmt = delete(Task).where(Task.id == task_id)
    await db.execute(del_stmt)
    await db.commit()

    # Log: TASK_DELETED
    await create_activity_log(
        db,
        user_id=current_user.id,
        task_id=task_id,
        action="TASK_DELETED",
        old_value=task.title
    )

    return {"message": "Task deleted"}

@router.get("/{task_id}/logs", response_model=list[ActivityLogResponse])
async def get_task_logs(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # Check if task exists
    q = await db.execute(select(Task).where(Task.id == task_id))
    task = q.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    # Fetch logs ordered by time (latest first)
    logs_stmt = (
        select(ActivityLog)
        .where(ActivityLog.task_id == task_id)
        .order_by(desc(ActivityLog.created_at))
    )

    result = await db.execute(logs_stmt)
    logs = result.scalars().all()

    return logs


@router.put("/{task_id}/assign/{user_id}", response_model=TaskResponse)
async def assign_task(
    task_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch task
    q = await db.execute(select(Task).where(Task.id == task_id))
    task = q.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")

    # Fetch user to assign
    u = await db.execute(select(User).where(User.id == user_id))
    user = u.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    old_assignee = str(task.assignee_id) if task.assignee_id else "None"

    # Assign user
    upd = (
        update(Task)
        .where(Task.id == task_id)
        .values(assignee_id=user_id)
        .returning(Task)
    )
    result = await db.execute(upd)
    await db.commit()

    updated = result.scalar_one()

    # Log: ASSIGNEE_UPDATED
    await create_activity_log(
        db,
        user_id=current_user.id,
        task_id=task_id,
        action="ASSIGNEE_UPDATED",
        old_value=old_assignee,
        new_value=str(user_id)
    )

    return updated


@router.put("/{task_id}/unassign", response_model=TaskResponse)
async def unassign_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch task
    q = await db.execute(select(Task).where(Task.id == task_id))
    task = q.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")

    if not task.assignee_id:
        raise HTTPException(400, "Task is already unassigned")

    old_assignee = str(task.assignee_id)

    # Remove assignee
    upd = (
        update(Task)
        .where(Task.id == task_id)
        .values(assignee_id=None)
        .returning(Task)
    )

    result = await db.execute(upd)
    await db.commit()

    updated = result.scalar_one()

    # Log: ASSIGNEE_REMOVED
    await create_activity_log(
        db,
        user_id=current_user.id,
        task_id=task_id,
        action="ASSIGNEE_REMOVED",
        old_value=old_assignee,
        new_value="None"
    )

    return updated
