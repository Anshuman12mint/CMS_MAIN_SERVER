from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.service import AttendanceService
from app.modules.auth.authorization import AuthorizationService
from app.modules.auth.dependencies import get_current_user
from app.modules.courses.repository import CourseRepository
from app.modules.courses.service import CourseService
from app.modules.fees.repository import FeeRepository
from app.modules.fees.service import FeeService
from app.modules.marks.repository import StudentMarkRepository
from app.modules.marks.service import StudentMarkService
from app.modules.reports.schemas import FeeSummary, StudentReport, TeacherReport
from app.modules.reports.service import ReportService
from app.modules.students.repository import StudentRepository
from app.modules.students.service import StudentService
from app.modules.subjects.repository import SubjectRepository
from app.modules.subjects.service import SubjectService
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.teachers.service import TeacherService
from app.modules.users.model import User


router = APIRouter(prefix="/api/reports", tags=["reports"], dependencies=[Depends(get_current_user)])


def get_report_service(session: Session = Depends(get_db_session)) -> ReportService:
    student_repository = StudentRepository(session)
    subject_repository = SubjectRepository(session)
    course_repository = CourseRepository(session)
    return ReportService(
        StudentService(student_repository, course_repository),
        TeacherService(
            TeacherRepository(session),
            course_repository,
            subject_repository,
            TeacherCourseRepository(session),
            TeacherSubjectRepository(session),
        ),
        AttendanceService(AttendanceRepository(session), student_repository),
        FeeService(FeeRepository(session), student_repository),
        StudentMarkService(StudentMarkRepository(session), student_repository, subject_repository),
        CourseService(course_repository),
        SubjectService(subject_repository, course_repository),
    )


def get_authorization_service(session: Session = Depends(get_db_session)) -> AuthorizationService:
    return AuthorizationService(session)


@router.get("/students/{student_id}", response_model=StudentReport)
def get_student_report(
    student_id: int,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> StudentReport:
    student = report_service.student_service.find_student(student_id)
    authorization_service.ensure_student_access(current_user, student)
    return report_service.get_student_report(student_id)


@router.get("/teachers/{teacher_id}", response_model=TeacherReport)
def get_teacher_report(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> TeacherReport:
    teacher = report_service.teacher_service.find_teacher(teacher_id)
    authorization_service.ensure_teacher_access(current_user, teacher)
    return report_service.get_teacher_report(teacher_id)


@router.get("/fees/summary", response_model=FeeSummary)
def get_fee_summary(
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> FeeSummary:
    authorization_service.ensure_admin_or_staff(current_user, "Only staff or admins can view fee summaries")
    return report_service.get_fee_summary()

