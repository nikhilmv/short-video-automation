from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name:Mapped[str] = mapped_column(
        String(100)
    )
    email:Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )
    password: Mapped[str] = mapped_column(
        String(255)
    )
    role: Mapped[str] = mapped_column(
        String(50), default="Member", nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="Active", nullable=True
    )
    gender: Mapped[str] = mapped_column(
        String(20), nullable=True
    )
    dob: Mapped[str] = mapped_column(
        String(50), nullable=True
    )