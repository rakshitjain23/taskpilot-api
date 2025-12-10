from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.ai_service import chat
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def ai_chat(payload: dict, 
                  user=Depends(get_current_user),
                  db: AsyncSession = Depends(get_db)):

    messages = payload.get("messages", [])
    result = await chat(messages, user.id, db)
    return result
