from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.attendance.model import Attendance


class AttendanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, attendance_id: int | None) -> Attendance | None:
        return None if attendance_id is None else self.session.get(Attendance, attendance_id)

    def find_by_student_id_ordered(self, student_id: int) -> list[Attendance]:
        return list(
            self.session.scalars(
                select(Attendance).where(Attendance.student_id == student_id).order_by(Attendance.date.desc())
            )
        )

    def find_all_ordered(self) -> list[Attendance]:
        return list(self.session.scalars(select(Attendance).order_by(Attendance.date.desc())))

    def save(self, attendance: Attendance) -> Attendance:
        self.session.add(attendance)
        self.session.flush()
        self.session.refresh(attendance)
        return attendance

    def delete(self, attendance: Attendance) -> None:
        self.session.delete(attendance)
        self.session.flush()

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Attendance)) or 0)

