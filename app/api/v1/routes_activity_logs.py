from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.db.session import get_db
from app.models.activity_log import ActivityLog
from app.models.task import Task
from app.schemas.activity_log_schema import ActivityLogResponse
from app.utils.dependencies import get_current_user  # ensures auth
from app.utils.pagination import get_pagination_params

router = APIRouter(prefix="/logs", tags=["Activity Logs"])


# Helper: base query builder (ActivityLog table)
def _base_logs_select():
    return select(ActivityLog)


# ---------------------------------------------------------
# GET /logs  - global logs with optional filters
# ---------------------------------------------------------
@router.get("", response_model=list[ActivityLogResponse])
async def get_logs(
    action: str | None = Query(None, description="Filter by action name, e.g. STATUS_CHANGED"),
    user_id: int | None = Query(None),
    project_id: int | None = Query(None),
    task_id: int | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    page: int | None = Query(1, ge=1),
    page_size: int | None = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user),
):
    offset, limit = get_pagination_params(page, page_size)

    stmt = _base_logs_select()

    # If project filter present, join via Task
    if project_id is not None:
        stmt = stmt.join(Task, ActivityLog.task_id == Task.id)
        stmt = stmt.where(Task.project_id == project_id)

    # Build other filters
    filters = []
    if action is not None:
        filters.append(ActivityLog.action == action)
    if user_id is not None:
        filters.append(ActivityLog.user_id == user_id)
    if task_id is not None:
        filters.append(ActivityLog.task_id == task_id)
    if date_from is not None:
        filters.append(ActivityLog.created_at >= date_from)
    if date_to is not None:
        filters.append(ActivityLog.created_at <= date_to)

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.order_by(desc(ActivityLog.created_at)).offset(offset).limit(limit)

    result = await db.execute(stmt)
    logs = result.scalars().all()
    return logs


# ---------------------------------------------------------
# GET /logs/tasks/{task_id} - logs for a specific task
# ---------------------------------------------------------
@router.get("/tasks/{task_id}", response_model=list[ActivityLogResponse])
async def get_task_logs(
    task_id: int,
    page: int | None = Query(1, ge=1),
    page_size: int | None = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user),
):
    offset, limit = get_pagination_params(page, page_size)

    # Ensure task exists (optional sanity check)
    res = await db.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    stmt = (
        select(ActivityLog)
        .where(ActivityLog.task_id == task_id)
        .order_by(desc(ActivityLog.created_at))
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------
# GET /logs/projects/{project_id} - logs for a project
# ---------------------------------------------------------
@router.get("/projects/{project_id}", response_model=list[ActivityLogResponse])
async def get_project_logs(
    project_id: int,
    page: int | None = Query(1, ge=1),
    page_size: int | None = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user),
):
    offset, limit = get_pagination_params(page, page_size)

    # join ActivityLog -> Task -> filter by project_id
    stmt = (
        select(ActivityLog)
        .join(Task, ActivityLog.task_id == Task.id)
        .where(Task.project_id == project_id)
        .order_by(desc(ActivityLog.created_at))
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------
# GET /logs/users/{user_id} - logs by a specific user (actions performed by user)
# ---------------------------------------------------------
@router.get("/users/{user_id}", response_model=list[ActivityLogResponse])
async def get_user_logs(
    user_id: int,
    page: int | None = Query(1, ge=1),
    page_size: int | None = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user),
):
    offset, limit = get_pagination_params(page, page_size)

    stmt = (
        select(ActivityLog)
        .where(ActivityLog.user_id == user_id)
        .order_by(desc(ActivityLog.created_at))
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()
