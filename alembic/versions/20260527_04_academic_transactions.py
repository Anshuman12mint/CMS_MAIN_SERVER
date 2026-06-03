"""academic transactions

Revision ID: 20260527_04
Revises: 20260527_03
Create Date: 2026-05-27 17:45:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260527_04"
down_revision = "20260527_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attendance",
        sa.Column("attendance_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.student_id"]),
        sa.PrimaryKeyConstraint("attendance_id"),
    )
    op.create_index("ix_attendance_student_date", "attendance", ["student_id", "date"], unique=False)

    op.create_table(
        "fees",
        sa.Column("fee_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.student_id"]),
        sa.PrimaryKeyConstraint("fee_id"),
    )
    op.create_index("ix_fees_student_due_date", "fees", ["student_id", "due_date"], unique=False)

    op.create_table(
        "student_marks",
        sa.Column("mark_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column("exam_type", sa.String(length=20), nullable=False),
        sa.Column("marks_obtained", sa.Numeric(5, 2), nullable=False),
        sa.Column("max_marks", sa.Numeric(5, 2), nullable=False),
        sa.Column("grade", sa.String(length=2), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.student_id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subject.subject_id"]),
        sa.PrimaryKeyConstraint("mark_id"),
    )


def downgrade() -> None:
    op.drop_table("student_marks")
    op.drop_index("ix_fees_student_due_date", table_name="fees")
    op.drop_table("fees")
    op.drop_index("ix_attendance_student_date", table_name="attendance")
    op.drop_table("attendance")
