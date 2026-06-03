from __future__ import annotations

from app.modules.admissions.schemas import AdmissionRead, AdmissionWriteRequest
from app.modules.students.schemas import StudentWriteRequest
from app.modules.students.service import StudentService


class AdmissionService:
    def __init__(self, student_service: StudentService) -> None:
        self.student_service = student_service

    def get_admissions(self) -> list[AdmissionRead]:
        return [self.student_to_admission(student) for student in self.student_service.get_students()]

    def get_admission(self, student_id: int) -> AdmissionRead:
        return self.student_to_admission(self.student_service.get_student(student_id))

    def create_admission(self, request: AdmissionWriteRequest) -> AdmissionRead:
        return self.student_to_admission(self.student_service.create_student(self.to_student_request(request)))

    def update_admission(self, student_id: int, request: AdmissionWriteRequest) -> AdmissionRead:
        current = self.student_service.get_student(student_id)
        student_request = self.to_student_request(request)
        student_request.student_code = current.student_code
        return self.student_to_admission(self.student_service.update_student(student_id, student_request))

    def delete_admission(self, student_id: int) -> None:
        self.student_service.delete_student(student_id)

    def to_student_request(self, request: AdmissionWriteRequest) -> StudentWriteRequest:
        return StudentWriteRequest(
            first_name=request.first_name,
            last_name=request.last_name,
            dob=request.dob,
            gender=request.gender,
            phone_number=request.phone_number,
            email=request.email,
            course_code=request.course_code,
            admission_date=request.admission_date,
            address=request.address,
            guardian_name=request.guardian_name,
            guardian_contact=request.guardian_contact,
            blood_group=request.blood_group,
        )

    def student_to_admission(self, student) -> AdmissionRead:
        return AdmissionRead(
            student_id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            dob=student.dob,
            gender=student.gender,
            phone_number=student.phone_number,
            email=student.email,
            course_code=student.course_code,
            admission_date=student.admission_date,
            address=student.address,
            guardian_name=student.guardian_name,
            guardian_contact=student.guardian_contact,
            blood_group=student.blood_group,
            created_at=student.created_at,
        )

