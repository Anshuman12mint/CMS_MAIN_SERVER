from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.admissions.service import AdmissionService
from app.modules.attendance.repository import AttendanceRepository
from app.modules.auth.dependencies import get_current_user, require_roles
from app.modules.courses.repository import CourseRepository
from app.modules.dashboard.schemas import DashboardSummary, UserDashboard
from app.modules.dashboard.service import DashboardService
from app.modules.fees.repository import FeeRepository
from app.modules.marks.repository import StudentMarkRepository
from app.modules.staff.repository import StaffRepository
from app.modules.students.repository import StudentRepository
from app.modules.students.service import StudentService
from app.modules.subjects.repository import SubjectRepository
from app.modules.teachers.repository import TeacherCourseRepository, TeacherRepository, TeacherSubjectRepository
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


def get_dashboard_service(session: Session = Depends(get_db_session)) -> DashboardService:
    student_repository = StudentRepository(session)
    course_repository = CourseRepository(session)
    admission_service = AdmissionService(StudentService(student_repository, course_repository))
    return DashboardService(
        student_repository,
        TeacherRepository(session),
        StaffRepository(session),
        course_repository,
        SubjectRepository(session),
        UserRepository(session),
        AttendanceRepository(session),
        FeeRepository(session),
        StudentMarkRepository(session),
        TeacherCourseRepository(session),
        TeacherSubjectRepository(session),
        admission_service,
    )


@router.get("", response_model=DashboardSummary)
def get_summary(
    current_user: User = Depends(require_roles("Admin", "Staff")),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummary:
    return dashboard_service.get_summary()


@router.get("/me", response_model=UserDashboard)
def get_my_dashboard(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> UserDashboard:
    return dashboard_service.get_dashboard_for_user(current_user)

