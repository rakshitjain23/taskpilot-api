from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from app.db.session import get_db
from app.models.comment import Comment
from app.models.task import Task
from app.schemas.comment_schema import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/comments", tags=["Comments"])

# CREATE COMMENT
@router.post("", response_model=CommentResponse)
async def create_comment(
    task_id: int,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check if task exists
    task_check = await db.execute(select(Task).where(Task.id == task_id))
    task = task_check.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    stmt = (
        insert(Comment)
        .values(
            content=data.content,
            task_id=task_id,
            user_id=current_user.id,
        )
        .returning(Comment)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one()

# GET ALL COMMENTS FOR A TASK

@router.get("/{task_id}", response_model=list[CommentResponse])
async def get_comments(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    stmt = select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at)

    result = await db.execute(stmt)
    return result.scalars().all()

# UPDATE COMMENT
@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch comment
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Only the user who wrote the comment can update
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot edit this comment")

    # Update comment
    upd = (
        update(Comment)
        .where(Comment.id == comment_id)
        .values(content=data.content)
        .returning(Comment)
    )

    result = await db.execute(upd)
    await db.commit()

    return result.scalar_one()

# DELETE COMMENT
@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot delete this comment")

    del_stmt = delete(Comment).where(Comment.id == comment_id)
    await db.execute(del_stmt)
    await db.commit()

    return {"message": "Comment deleted successfully"}
