from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Course(Base):
    __tablename__ = "course"

    course_code: Mapped[str] = mapped_column("course_code", String(10), primary_key=True)
    course_name: Mapped[str] = mapped_column("course_name", String(100), nullable=False)
    course_description: Mapped[str | None] = mapped_column("course_description", Text, nullable=True)

