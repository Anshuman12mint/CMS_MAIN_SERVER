from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.marks.model import StudentMark


class StudentMarkRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, mark_id: int | None) -> StudentMark | None:
        return None if mark_id is None else self.session.get(StudentMark, mark_id)

    def find_by_student_id_ordered(self, student_id: int) -> list[StudentMark]:
        return list(
            self.session.scalars(
                select(StudentMark).where(StudentMark.student_id == student_id).order_by(StudentMark.exam_date.desc())
            )
        )

    def find_all_ordered(self) -> list[StudentMark]:
        return list(self.session.scalars(select(StudentMark).order_by(StudentMark.exam_date.desc())))

    def save(self, mark: StudentMark) -> StudentMark:
        self.session.add(mark)
        self.session.flush()
        self.session.refresh(mark)
        return mark

    def delete(self, mark: StudentMark) -> None:
        self.session.delete(mark)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(StudentMark)) or 0)

