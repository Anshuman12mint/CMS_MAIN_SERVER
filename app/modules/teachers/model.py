from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Teacher(Base):
    __tablename__ = "teacher"

    teacher_id: Mapped[int] = mapped_column("teacher_id", Integer, primary_key=True, autoincrement=True)
    teacher_code: Mapped[str] = mapped_column("teacher_code", String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column("first_name", String(50), nullable=False)
    last_name: Mapped[str] = mapped_column("last_name", String(50), nullable=False)
    dob: Mapped[date] = mapped_column("dob", Date, nullable=False)
    gender: Mapped[str] = mapped_column("gender", String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column("phone_number", String(15), unique=True, nullable=False)
    email: Mapped[str] = mapped_column("email", String(100), unique=True, nullable=False)
    hire_date: Mapped[date] = mapped_column("hire_date", Date, nullable=False)
    department: Mapped[str | None] = mapped_column("department", String(100), nullable=True)
    address: Mapped[str | None] = mapped_column("address", Text, nullable=True)
    qualification: Mapped[str | None] = mapped_column("qualification", String(100), nullable=True)
    salary: Mapped[Decimal | None] = mapped_column("salary", Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())


class TeacherCourse(Base):
    __tablename__ = "teacher_course"

    teacher_id: Mapped[int] = mapped_column("teacher_id", ForeignKey("teacher.teacher_id"), primary_key=True)
    course_code: Mapped[str] = mapped_column("course_code", ForeignKey("course.course_code"), primary_key=True)

    teacher = relationship("Teacher")
    course = relationship("Course")


class TeacherSubject(Base):
    __tablename__ = "teacher_subject"

    teacher_id: Mapped[int] = mapped_column("teacher_id", ForeignKey("teacher.teacher_id"), primary_key=True)
    subject_id: Mapped[int] = mapped_column("subject_id", ForeignKey("subject.subject_id"), primary_key=True)

    teacher = relationship("Teacher")
    subject = relationship("Subject")

