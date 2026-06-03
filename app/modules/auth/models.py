from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id: Mapped[int] = mapped_column("refresh_token_id", Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("users.user_id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column("token_hash", String(128), nullable=False, unique=True)
    user_agent: Mapped[str | None] = mapped_column("user_agent", String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column("ip_address", String(64), nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column("issued_at", DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column("expires_at", DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column("revoked_at", DateTime(timezone=True), nullable=True, index=True)

    user = relationship("User")

