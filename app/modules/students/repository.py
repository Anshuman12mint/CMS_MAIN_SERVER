from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.students.model import Student


class StudentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, student_id: int | None) -> Student | None:
        return None if student_id is None else self.session.get(Student, student_id)

    def find_by_student_code(self, student_code: str | None) -> Student | None:
        if student_code is None:
            return None
        return self.session.scalar(select(Student).where(func.lower(Student.student_code) == student_code.strip().lower()))

    def exists_by_id(self, student_id: int | None) -> bool:
        if student_id is None:
            return False
        return bool(self.session.scalar(select(func.count()).select_from(Student).where(Student.student_id == student_id)))

    def exists_by_student_code(self, student_code: str | None, exclude_student_id: int | None = None) -> bool:
        if student_code is None:
            return False
        statement = select(func.count()).select_from(Student).where(func.lower(Student.student_code) == student_code.strip().lower())
        if exclude_student_id is not None:
            statement = statement.where(Student.student_id != exclude_student_id)
        return bool(self.session.scalar(statement))

    def find_by_course_code_ordered(self, course_code: str) -> list[Student]:
        return list(
            self.session.scalars(
                select(Student).where(Student.course_code == course_code).order_by(Student.admission_date.desc())
            )
        )

    def find_all_ordered(self) -> list[Student]:
        return list(self.session.scalars(select(Student).order_by(Student.admission_date.desc())))

    def save(self, student: Student) -> Student:
        self.session.add(student)
        self.session.flush()
        self.session.refresh(student)
        return student

    def delete(self, student: Student) -> None:
        self.session.delete(student)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Student)) or 0)

