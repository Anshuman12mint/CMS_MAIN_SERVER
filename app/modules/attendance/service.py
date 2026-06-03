from __future__ import annotations

from fastapi import HTTPException, status

from app.common import validators
from app.modules.attendance.model import Attendance
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.schemas import AttendanceRead, AttendanceWriteRequest
from app.modules.students.model import Student
from app.modules.students.repository import StudentRepository


class AttendanceService:
    def __init__(self, attendance_repository: AttendanceRepository, student_repository: StudentRepository) -> None:
        self.attendance_repository = attendance_repository
        self.student_repository = student_repository

    def get_attendance(self, student_id: int | None, status_value: str | None = None, sort_dir: str = "desc") -> list[AttendanceRead]:
        rows = (
            self.attendance_repository.find_all_ordered()
            if student_id is None
            else self.attendance_repository.find_by_student_id_ordered(student_id)
        )
        items = [self.to_read(row) for row in rows]
        if validators.has_text(status_value):
            normalized_status = status_value.strip().lower()
            items = [item for item in items if (item.status or "").strip().lower() == normalized_status]
        return items if (sort_dir or "desc").strip().lower() != "asc" else list(reversed(items))

    def get_attendance_by_id(self, attendance_id: int) -> AttendanceRead:
        return self.to_read(self.find_attendance(attendance_id))

    def create_attendance(self, request: AttendanceWriteRequest) -> AttendanceRead:
        attendance = Attendance()
        self.apply_attendance(attendance, request)
        return self.to_read(self.attendance_repository.save(attendance))

    def update_attendance(self, attendance_id: int, request: AttendanceWriteRequest) -> AttendanceRead:
        attendance = self.find_attendance(attendance_id)
        self.apply_attendance(attendance, request)
        return self.to_read(self.attendance_repository.save(attendance))

    def delete_attendance(self, attendance_id: int) -> None:
        self.attendance_repository.delete(self.find_attendance(attendance_id))

    def apply_attendance(self, attendance: Attendance, request: AttendanceWriteRequest) -> None:
        student = self.find_student(request.student_id)
        validators.require(request.date is not None, "date is required")
        assert request.date is not None
        attendance.student = student
        attendance.student_id = student.student_id
        attendance.date = request.date
        attendance.status = validators.normalize_required_choice(request.status, validators.ATTENDANCE_STATUSES, "status")

    def find_attendance(self, attendance_id: int | None) -> Attendance:
        attendance = self.attendance_repository.find_by_id(attendance_id)
        if attendance is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
        return attendance

    def find_student(self, student_id: int | None) -> Student:
        student = self.student_repository.find_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def to_read(self, attendance: Attendance) -> AttendanceRead:
        return AttendanceRead(
            attendance_id=attendance.attendance_id,
            student_id=attendance.student.student_id if attendance.student is not None else attendance.student_id,
            date=attendance.date,
            status=attendance.status,
        )

