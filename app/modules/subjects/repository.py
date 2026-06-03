from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.subjects.model import Subject


class SubjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, subject_id: int | None) -> Subject | None:
        return None if subject_id is None else self.session.get(Subject, subject_id)

    def find_by_course_code(self, course_code: str) -> list[Subject]:
        return list(
            self.session.scalars(
                select(Subject).where(Subject.course_code == course_code).order_by(Subject.subject_code.asc())
            )
        )

    def find_all(self) -> list[Subject]:
        return list(self.session.scalars(select(Subject).order_by(Subject.course_code.asc(), Subject.subject_code.asc())))

    def exists_by_subject_code(self, subject_code: str | None, exclude_subject_id: int | None = None) -> bool:
        if subject_code is None:
            return False
        statement = select(func.count()).select_from(Subject).where(func.lower(Subject.subject_code) == subject_code.strip().lower())
        if exclude_subject_id is not None:
            statement = statement.where(Subject.subject_id != exclude_subject_id)
        return bool(self.session.scalar(statement))

    def save(self, subject: Subject) -> Subject:
        self.session.add(subject)
        self.session.flush()
        self.session.refresh(subject)
        return subject

    def delete(self, subject: Subject) -> None:
        self.session.delete(subject)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Subject)) or 0)

