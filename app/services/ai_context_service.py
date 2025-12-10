from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.task import Task
from app.models.comment import Comment


async def build_user_context(user_id: int, db: AsyncSession):
    """
    Gather all user-related DB information to send as AI context.
    """

    user = await db.scalar(select(User).where(User.id == user_id))

    workspaces = await db.scalars(
        select(Workspace).where(Workspace.owner_id == user_id)
    )
    workspaces = list(workspaces)

    projects = await db.scalars(
        select(Project).where(Project.workspace_id.in_([w.id for w in workspaces]))
    )
    projects = list(projects)

    tasks = await db.scalars(
        select(Task).where(Task.project_id.in_([p.id for p in projects]))
    )
    tasks = list(tasks)

    comments = await db.scalars(
        select(Comment).where(Comment.task_id.in_([t.id for t in tasks]))
    )
    comments = list(comments)

    # Build a structured summary
    return {
        "user": {"id": user.id, "email": user.email},
        "workspaces": [
            {
                "id": w.id,
                "name": w.name,
                "created_at": str(w.created_at),
            }
            for w in workspaces
        ],
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "workspace_id": p.workspace_id,
            }
            for p in projects
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "project_id": t.project_id,
            }
            for t in tasks
        ],
        "comments": [
            {
                "id": c.id,
                "text": c.text,
                "task_id": c.task_id,
            }
            for c in comments
        ],
    }
