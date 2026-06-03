from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.courses.model import Course


class CourseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, course_code: str | None) -> Course | None:
        return None if course_code is None else self.session.get(Course, course_code)

    def exists_by_id(self, course_code: str | None) -> bool:
        return self.find_by_id(course_code) is not None

    def find_all(self) -> list[Course]:
        return list(self.session.scalars(select(Course).order_by(Course.course_code.asc())))

    def save(self, course: Course) -> Course:
        self.session.add(course)
        self.session.flush()
        self.session.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.session.delete(course)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Course)) or 0)

