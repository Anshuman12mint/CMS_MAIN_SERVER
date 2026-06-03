from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (Index("ix_attendance_student_date", "student_id", "date"),)

    attendance_id: Mapped[int] = mapped_column("attendance_id", Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column("student_id", ForeignKey("student.student_id"), nullable=False)
    date: Mapped[date] = mapped_column("date", Date, nullable=False)
    status: Mapped[str] = mapped_column("status", String(20), nullable=False)

    student = relationship("Student")

