from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.teachers.model import Teacher, TeacherCourse, TeacherSubject


class TeacherRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, teacher_id: int | None) -> Teacher | None:
        return None if teacher_id is None else self.session.get(Teacher, teacher_id)

    def find_by_teacher_code(self, teacher_code: str | None) -> Teacher | None:
        if teacher_code is None:
            return None
        return self.session.scalar(select(Teacher).where(func.lower(Teacher.teacher_code) == teacher_code.strip().lower()))

    def exists_by_id(self, teacher_id: int | None) -> bool:
        if teacher_id is None:
            return False
        return bool(self.session.scalar(select(func.count()).select_from(Teacher).where(Teacher.teacher_id == teacher_id)))

    def exists_by_teacher_code(self, teacher_code: str | None, exclude_teacher_id: int | None = None) -> bool:
        if teacher_code is None:
            return False
        statement = select(func.count()).select_from(Teacher).where(func.lower(Teacher.teacher_code) == teacher_code.strip().lower())
        if exclude_teacher_id is not None:
            statement = statement.where(Teacher.teacher_id != exclude_teacher_id)
        return bool(self.session.scalar(statement))

    def find_all(self) -> list[Teacher]:
        return list(self.session.scalars(select(Teacher)))

    def save(self, teacher: Teacher) -> Teacher:
        self.session.add(teacher)
        self.session.flush()
        self.session.refresh(teacher)
        return teacher

    def delete(self, teacher: Teacher) -> None:
        self.session.delete(teacher)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Teacher)) or 0)


class TeacherCourseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_teacher_id(self, teacher_id: int) -> list[TeacherCourse]:
        return list(self.session.scalars(select(TeacherCourse).where(TeacherCourse.teacher_id == teacher_id)))

    def delete_by_teacher_id(self, teacher_id: int) -> None:
        self.session.execute(delete(TeacherCourse).where(TeacherCourse.teacher_id == teacher_id))
        self.session.flush()

    def save_all(self, assignments: list[TeacherCourse]) -> list[TeacherCourse]:
        self.session.add_all(assignments)
        self.session.flush()
        return assignments


class TeacherSubjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_teacher_id(self, teacher_id: int) -> list[TeacherSubject]:
        return list(self.session.scalars(select(TeacherSubject).where(TeacherSubject.teacher_id == teacher_id)))

    def delete_by_teacher_id(self, teacher_id: int) -> None:
        self.session.execute(delete(TeacherSubject).where(TeacherSubject.teacher_id == teacher_id))
        self.session.flush()

    def save_all(self, assignments: list[TeacherSubject]) -> list[TeacherSubject]:
        self.session.add_all(assignments)
        self.session.flush()
        return assignments

