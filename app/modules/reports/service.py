from __future__ import annotations

from decimal import Decimal

from app.modules.attendance.service import AttendanceService
from app.modules.courses.service import CourseService
from app.modules.fees.schemas import FeeRead
from app.modules.fees.service import FeeService
from app.modules.marks.service import StudentMarkService
from app.modules.reports.schemas import FeeSummary, StudentReport, TeacherReport
from app.modules.students.service import StudentService
from app.modules.subjects.service import SubjectService
from app.modules.teachers.service import TeacherService


class ReportService:
    def __init__(
        self,
        student_service: StudentService,
        teacher_service: TeacherService,
        attendance_service: AttendanceService,
        fee_service: FeeService,
        student_mark_service: StudentMarkService,
        course_service: CourseService,
        subject_service: SubjectService,
    ) -> None:
        self.student_service = student_service
        self.teacher_service = teacher_service
        self.attendance_service = attendance_service
        self.fee_service = fee_service
        self.student_mark_service = student_mark_service
        self.course_service = course_service
        self.subject_service = subject_service

    def get_student_report(self, student_id: int) -> StudentReport:
        student = self.student_service.get_student(student_id)
        attendance = self.attendance_service.get_attendance(student_id)
        fees = self.fee_service.get_fees(student_id)
        marks = self.student_mark_service.get_marks(student_id)

        present_days = sum(1 for item in attendance if (item.status or "").lower() == "present")
        absent_days = sum(1 for item in attendance if (item.status or "").lower() == "absent")

        return StudentReport(
            student=student,
            present_days=present_days,
            absent_days=absent_days,
            total_fees=self.sum_fees(fees, lambda fee: True),
            paid_fees=self.sum_fees(fees, lambda fee: (fee.status or "").lower() == "paid"),
            pending_fees_amount=self.sum_fees(fees, lambda fee: (fee.status or "").lower() == "pending"),
            attendance=attendance,
            fees=fees,
            marks=marks,
        )

    def get_teacher_report(self, teacher_id: int) -> TeacherReport:
        teacher = self.teacher_service.get_teacher(teacher_id)
        courses = [self.course_service.get_course(course_code) for course_code in teacher.course_codes]
        subjects = [self.subject_service.get_subject(subject_id) for subject_id in teacher.subject_ids]
        return TeacherReport(teacher=teacher, courses=courses, subjects=subjects)

    def get_fee_summary(self) -> FeeSummary:
        fees = self.fee_service.get_fees(None)
        pending_fees = [fee for fee in fees if (fee.status or "").lower() == "pending"]
        return FeeSummary(
            paid_count=sum(1 for fee in fees if (fee.status or "").lower() == "paid"),
            pending_count=len(pending_fees),
            paid_amount=self.sum_fees(fees, lambda fee: (fee.status or "").lower() == "paid"),
            pending_amount=self.sum_fees(fees, lambda fee: (fee.status or "").lower() == "pending"),
            pending_fees=pending_fees,
        )

    def sum_fees(self, fees: list[FeeRead], predicate) -> Decimal:
        total = Decimal("0")
        for fee in fees:
            if predicate(fee) and fee.amount is not None:
                total += fee.amount
        return total

