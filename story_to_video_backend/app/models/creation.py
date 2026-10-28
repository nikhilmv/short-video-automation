from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.core.database import Base


class Creation(Base):
    __tablename__ = "creation"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )
    user_id:Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        index=True
    )
    story_text:Mapped[str] = mapped_column(
        String(1000)
    ) 
    # "pending", "processing", "completed", "failed" 
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=True
    ) 
    video_url: Mapped[str] = mapped_column(
        String(255), nullable=True
    )

