from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Subject(Base):
    __tablename__ = "subject"

    subject_id: Mapped[int] = mapped_column("subject_id", Integer, primary_key=True, autoincrement=True)
    subject_name: Mapped[str] = mapped_column("subject_name", String(100), nullable=False)
    subject_code: Mapped[str] = mapped_column("subject_code", String(10), unique=True, nullable=False, index=True)
    course_code: Mapped[str] = mapped_column("course_code", String(10), ForeignKey("course.course_code"), nullable=False, index=True)
    subject_description: Mapped[str | None] = mapped_column("subject_description", Text, nullable=True)

