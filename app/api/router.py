from __future__ import annotations

from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.admissions.router import router as admissions_router
from app.modules.attendance.router import router as attendance_router
from app.modules.auth.router import router as auth_router
from app.modules.courses.router import router as courses_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.fees.router import router as fees_router
from app.modules.marks.router import router as marks_router
from app.modules.reports.router import router as reports_router
from app.modules.staff.router import router as staff_router
from app.modules.students.router import router as students_router
from app.modules.subjects.router import router as subjects_router
from app.modules.teachers.router import router as teachers_router
from app.modules.users.router import router as users_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(courses_router)
api_router.include_router(subjects_router)
api_router.include_router(students_router)
api_router.include_router(admissions_router)
api_router.include_router(attendance_router)
api_router.include_router(fees_router)
api_router.include_router(marks_router)
api_router.include_router(staff_router)
api_router.include_router(teachers_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)

