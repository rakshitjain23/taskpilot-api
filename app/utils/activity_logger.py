from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.models.activity_log import ActivityLog


async def create_activity_log(
    db: AsyncSession,
    *,
    user_id: int,
    task_id: int | None,
    action: str,
    old_value: str | None = None,
    new_value: str | None = None
):
    """
    Create an activity log entry.
    
    Parameters:
    - user_id: kis user ne action kiya
    - task_id: kis task par action kiya (comment/update/create)
    - action: action type string
    - old_value: purana value (optional)
    - new_value: naya value (optional)
    """

    stmt = (
        insert(ActivityLog)
        .values(
            user_id=user_id,
            task_id=task_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
        )
    )

    await db.execute(stmt)
    await db.commit()
