from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column("user_id", Integer, primary_key=True, autoincrement=True)
    legacy_username: Mapped[str | None] = mapped_column("username", String(50), unique=True, nullable=True)
    login_id: Mapped[str] = mapped_column("login_id", String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column("password_hash", String(255), nullable=False)
    email: Mapped[str] = mapped_column("email", String(100), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column("role", String(20), nullable=False, index=True)
    account_status: Mapped[str] = mapped_column("account_status", String(20), nullable=False, default="ACTIVE")
    registered_at: Mapped[datetime | None] = mapped_column("registered_at", DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column("last_login_at", DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    student_id: Mapped[int | None] = mapped_column("student_id", Integer, unique=True, nullable=True)
    teacher_id: Mapped[int | None] = mapped_column("teacher_id", Integer, unique=True, nullable=True)
    staff_id: Mapped[int | None] = mapped_column("staff_id", Integer, unique=True, nullable=True)

    @property
    def username(self) -> str:
        return self.login_id

    @username.setter
    def username(self, value: str) -> None:
        self.login_id = value
        self.legacy_username = value

    @property
    def profile_type(self) -> str | None:
        if self.student_id is not None:
            return "Student"
        if self.teacher_id is not None:
            return "Teacher"
        if self.staff_id is not None:
            return "Staff"
        return None

    @property
    def profile_id(self) -> int | None:
        if self.student_id is not None:
            return self.student_id
        if self.teacher_id is not None:
            return self.teacher_id
        if self.staff_id is not None:
            return self.staff_id
        return None

