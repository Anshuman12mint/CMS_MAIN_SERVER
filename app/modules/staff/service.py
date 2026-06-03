from __future__ import annotations

import secrets

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.modules.staff.model import Staff
from app.modules.staff.repository import StaffRepository
from app.modules.staff.schemas import StaffRead, StaffWriteRequest


class StaffService:
    def __init__(self, staff_repository: StaffRepository) -> None:
        self.staff_repository = staff_repository

    def get_staff_members(self) -> list[StaffRead]:
        return [self.to_read(staff) for staff in self.staff_repository.find_all()]

    def get_staff(self, staff_id: int) -> StaffRead:
        return self.to_read(self.find_staff(staff_id))

    def create_staff(self, request: StaffWriteRequest) -> StaffRead:
        staff = Staff()
        self.apply_staff(staff, request)
        return self.to_read(self.staff_repository.save(staff))

    def update_staff(self, staff_id: int, request: StaffWriteRequest) -> StaffRead:
        staff = self.find_staff(staff_id)
        self.apply_staff(staff, request)
        return self.to_read(self.staff_repository.save(staff))

    def delete_staff(self, staff_id: int) -> None:
        self.staff_repository.delete(self.find_staff(staff_id))

    def find_staff(self, staff_id: int | None) -> Staff:
        staff = self.staff_repository.find_by_id(staff_id)
        if staff is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
        return staff

    def apply_staff(self, staff: Staff, request: StaffWriteRequest) -> None:
        validators.require_text(request.first_name, "firstName")
        validators.require_text(request.last_name, "lastName")
        validators.require(request.dob is not None, "dob is required")
        validators.require(request.hire_date is not None, "hireDate is required")
        validators.require_text(request.phone_number, "phoneNumber")
        validators.require_text(str(request.email) if request.email is not None else None, "email")
        staff_code = helpers.normalize_code(request.staff_code) or staff.staff_code or self.generate_staff_code(staff.staff_id)
        if self.staff_repository.exists_by_staff_code(staff_code, exclude_staff_id=staff.staff_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="staffCode already exists")

        assert request.dob is not None
        assert request.hire_date is not None
        staff.staff_code = staff_code
        staff.first_name = helpers.trim_to_none(request.first_name) or ""
        staff.last_name = helpers.trim_to_none(request.last_name) or ""
        staff.dob = request.dob
        staff.gender = validators.normalize_required_choice(request.gender, validators.GENDERS, "gender")
        staff.phone_number = helpers.trim_to_none(request.phone_number) or ""
        staff.email = str(request.email).lower()
        staff.hire_date = request.hire_date
        staff.role = validators.normalize_required_choice(request.role, validators.STAFF_ROLES, "role")
        staff.department = helpers.trim_to_none(request.department)
        staff.address = helpers.trim_to_none(request.address)
        staff.salary = request.salary

    def generate_staff_code(self, staff_id: int | None) -> str:
        if staff_id is not None:
            return f"STF-{staff_id:05d}"
        while True:
            candidate = "STF-" + secrets.token_hex(4).upper()
            if not self.staff_repository.exists_by_staff_code(candidate):
                return candidate

    def to_read(self, staff: Staff) -> StaffRead:
        return StaffRead(
            staff_id=staff.staff_id,
            staff_code=staff.staff_code,
            first_name=staff.first_name,
            last_name=staff.last_name,
            dob=staff.dob,
            gender=staff.gender,
            phone_number=staff.phone_number,
            email=staff.email,
            hire_date=staff.hire_date,
            role=staff.role,
            department=staff.department,
            address=staff.address,
            salary=staff.salary,
            created_at=staff.created_at,
        )

