from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Fee(Base):
    __tablename__ = "fees"
    __table_args__ = (Index("ix_fees_student_due_date", "student_id", "due_date"),)

    fee_id: Mapped[int] = mapped_column("fee_id", Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column("student_id", ForeignKey("student.student_id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column("amount", Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column("status", String(20), nullable=False)
    due_date: Mapped[date] = mapped_column("due_date", Date, nullable=False)

    student = relationship("Student")

