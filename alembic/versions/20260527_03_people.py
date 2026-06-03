"""people profiles

Revision ID: 20260527_03
Revises: 20260527_02
Create Date: 2026-05-27 17:20:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260527_03"
down_revision = "20260527_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student",
        sa.Column("student_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_code", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("phone_number", sa.String(length=15), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("course_code", sa.String(length=10), nullable=False),
        sa.Column("admission_date", sa.Date(), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("guardian_name", sa.String(length=100), nullable=True),
        sa.Column("guardian_contact", sa.String(length=15), nullable=True),
        sa.Column("blood_group", sa.String(length=3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["course_code"], ["course.course_code"]),
        sa.PrimaryKeyConstraint("student_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("student_code"),
    )
    op.create_index(op.f("ix_student_course_code"), "student", ["course_code"], unique=False)
    op.create_index(op.f("ix_student_student_code"), "student", ["student_code"], unique=False)

    op.create_table(
        "teacher",
        sa.Column("teacher_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_code", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("phone_number", sa.String(length=15), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("qualification", sa.String(length=100), nullable=True),
        sa.Column("salary", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("teacher_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("teacher_code"),
    )
    op.create_index(op.f("ix_teacher_teacher_code"), "teacher", ["teacher_code"], unique=False)

    op.create_table(
        "staff",
        sa.Column("staff_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("staff_code", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("phone_number", sa.String(length=15), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("salary", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("staff_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("staff_code"),
    )
    op.create_index(op.f("ix_staff_staff_code"), "staff", ["staff_code"], unique=False)

    op.create_table(
        "teacher_course",
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("course_code", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["course_code"], ["course.course_code"]),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher.teacher_id"]),
        sa.PrimaryKeyConstraint("teacher_id", "course_code"),
    )

    op.create_table(
        "teacher_subject",
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subject.subject_id"]),
        sa.ForeignKeyConstraint(["teacher_id"], ["teacher.teacher_id"]),
        sa.PrimaryKeyConstraint("teacher_id", "subject_id"),
    )


def downgrade() -> None:
    op.drop_table("teacher_subject")
    op.drop_table("teacher_course")
    op.drop_index(op.f("ix_staff_staff_code"), table_name="staff")
    op.drop_table("staff")
    op.drop_index(op.f("ix_teacher_teacher_code"), table_name="teacher")
    op.drop_table("teacher")
    op.drop_index(op.f("ix_student_student_code"), table_name="student")
    op.drop_index(op.f("ix_student_course_code"), table_name="student")
    op.drop_table("student")
