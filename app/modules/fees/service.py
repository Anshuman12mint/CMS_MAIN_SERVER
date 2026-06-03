from __future__ import annotations

from fastapi import HTTPException, status

from app.common import validators
from app.modules.fees.model import Fee
from app.modules.fees.repository import FeeRepository
from app.modules.fees.schemas import FeeRead, FeeWriteRequest
from app.modules.students.model import Student
from app.modules.students.repository import StudentRepository


class FeeService:
    def __init__(self, fee_repository: FeeRepository, student_repository: StudentRepository) -> None:
        self.fee_repository = fee_repository
        self.student_repository = student_repository

    def get_fees(self, student_id: int | None, status_value: str | None = None, sort_dir: str = "desc") -> list[FeeRead]:
        rows = self.fee_repository.find_all_ordered() if student_id is None else self.fee_repository.find_by_student_id_ordered(student_id)
        items = [self.to_read(row) for row in rows]
        if validators.has_text(status_value):
            normalized_status = status_value.strip().lower()
            items = [item for item in items if (item.status or "").strip().lower() == normalized_status]
        return items if (sort_dir or "desc").strip().lower() != "asc" else list(reversed(items))

    def get_fee(self, fee_id: int) -> FeeRead:
        return self.to_read(self.find_fee(fee_id))

    def create_fee(self, request: FeeWriteRequest) -> FeeRead:
        fee = Fee()
        self.apply_fee(fee, request)
        return self.to_read(self.fee_repository.save(fee))

    def update_fee(self, fee_id: int, request: FeeWriteRequest) -> FeeRead:
        fee = self.find_fee(fee_id)
        self.apply_fee(fee, request)
        return self.to_read(self.fee_repository.save(fee))

    def delete_fee(self, fee_id: int) -> None:
        self.fee_repository.delete(self.find_fee(fee_id))

    def apply_fee(self, fee: Fee, request: FeeWriteRequest) -> None:
        student = self.find_student(request.student_id)
        validators.require(request.amount is not None, "amount is required")
        validators.require(request.due_date is not None, "dueDate is required")
        assert request.amount is not None
        assert request.due_date is not None
        fee.student = student
        fee.student_id = student.student_id
        fee.amount = request.amount
        fee.status = validators.normalize_required_choice(request.status, validators.FEE_STATUSES, "status")
        fee.due_date = request.due_date

    def find_fee(self, fee_id: int | None) -> Fee:
        fee = self.fee_repository.find_by_id(fee_id)
        if fee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee not found")
        return fee

    def find_student(self, student_id: int | None) -> Student:
        student = self.student_repository.find_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def to_read(self, fee: Fee) -> FeeRead:
        return FeeRead(
            fee_id=fee.fee_id,
            student_id=fee.student.student_id if fee.student is not None else fee.student_id,
            amount=fee.amount,
            status=fee.status,
            due_date=fee.due_date,
        )

