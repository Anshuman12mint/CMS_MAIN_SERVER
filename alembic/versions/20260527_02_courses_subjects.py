"""courses subjects

Revision ID: 20260527_02
Revises: 20260527_01
Create Date: 2026-05-27 16:55:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260527_02"
down_revision = "20260527_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course",
        sa.Column("course_code", sa.String(length=10), nullable=False),
        sa.Column("course_name", sa.String(length=100), nullable=False),
        sa.Column("course_description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("course_code"),
    )

    op.create_table(
        "subject",
        sa.Column("subject_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_name", sa.String(length=100), nullable=False),
        sa.Column("subject_code", sa.String(length=10), nullable=False),
        sa.Column("course_code", sa.String(length=10), nullable=False),
        sa.Column("subject_description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["course_code"], ["course.course_code"]),
        sa.PrimaryKeyConstraint("subject_id"),
        sa.UniqueConstraint("subject_code"),
    )
    op.create_index(op.f("ix_subject_course_code"), "subject", ["course_code"], unique=False)
    op.create_index(op.f("ix_subject_subject_code"), "subject", ["subject_code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_subject_subject_code"), table_name="subject")
    op.drop_index(op.f("ix_subject_course_code"), table_name="subject")
    op.drop_table("subject")
    op.drop_table("course")
