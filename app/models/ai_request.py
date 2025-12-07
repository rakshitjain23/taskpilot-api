from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum

from app.db.base import Base

class AIRequestType(str, enum.Enum):
    SUMMARY = "SUMMARY"
    DESCRIPTION = "DESCRIPTION"

class AIRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

class AIRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    type: Mapped[AIRequestType] = mapped_column(Enum(AIRequestType))
    status: Mapped[AIRequestStatus] = mapped_column(Enum(AIRequestStatus), default=AIRequestStatus.PENDING)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))

    result_text: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User")
    task = relationship("Task")
    project = relationship("Project")
