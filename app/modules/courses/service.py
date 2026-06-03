from __future__ import annotations

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.modules.courses.model import Course
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseRead, CourseWriteRequest


class CourseService:
    def __init__(self, course_repository: CourseRepository) -> None:
        self.course_repository = course_repository

    def get_courses(self) -> list[CourseRead]:
        return [self.to_read(course) for course in self.course_repository.find_all()]

    def get_course(self, course_code: str) -> CourseRead:
        return self.to_read(self.find_course(course_code))

    def create_course(self, request: CourseWriteRequest) -> CourseRead:
        course_code = helpers.normalize_code(request.course_code)
        course_name = helpers.trim_to_none(request.course_name)
        validators.require_text(course_code, "courseCode")
        validators.require_text(course_name, "courseName")
        assert course_code is not None
        assert course_name is not None
        validators.require(not self.course_repository.exists_by_id(course_code), "Course already exists")

        course = Course()
        course.course_code = course_code
        course.course_name = course_name
        course.course_description = helpers.trim_to_none(request.course_description)
        return self.to_read(self.course_repository.save(course))

    def update_course(self, course_code: str, request: CourseWriteRequest) -> CourseRead:
        course = self.find_course(course_code)
        course_name = helpers.trim_to_none(request.course_name)
        validators.require_text(course_name, "courseName")
        assert course_name is not None
        course.course_name = course_name
        course.course_description = helpers.trim_to_none(request.course_description)
        return self.to_read(self.course_repository.save(course))

    def delete_course(self, course_code: str) -> None:
        self.course_repository.delete(self.find_course(course_code))

    def find_course(self, course_code: str | None) -> Course:
        course = self.course_repository.find_by_id(helpers.normalize_code(course_code))
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return course

    def to_read(self, course: Course) -> CourseRead:
        return CourseRead(
            course_code=course.course_code,
            course_name=course.course_name,
            course_description=course.course_description,
        )

