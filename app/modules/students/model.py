from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Student(Base):
    __tablename__ = "student"

    student_id: Mapped[int] = mapped_column("student_id", Integer, primary_key=True, autoincrement=True)
    student_code: Mapped[str] = mapped_column("student_code", String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column("first_name", String(50), nullable=False)
    last_name: Mapped[str] = mapped_column("last_name", String(50), nullable=False)
    dob: Mapped[date] = mapped_column("dob", Date, nullable=False)
    gender: Mapped[str] = mapped_column("gender", String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column("phone_number", String(15), unique=True, nullable=False)
    email: Mapped[str] = mapped_column("email", String(100), unique=True, nullable=False)
    course_code: Mapped[str] = mapped_column("course_code", String(10), ForeignKey("course.course_code"), nullable=False, index=True)
    admission_date: Mapped[date] = mapped_column("admission_date", Date, nullable=False)
    address: Mapped[str | None] = mapped_column("address", Text, nullable=True)
    guardian_name: Mapped[str | None] = mapped_column("guardian_name", String(100), nullable=True)
    guardian_contact: Mapped[str | None] = mapped_column("guardian_contact", String(15), nullable=True)
    blood_group: Mapped[str | None] = mapped_column("blood_group", String(3), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

