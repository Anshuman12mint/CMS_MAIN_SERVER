from __future__ import annotations

from fastapi import HTTPException, status

from app.common import helpers, validators
from app.core.security import hash_password
from app.modules.staff.repository import StaffRepository
from app.modules.students.repository import StudentRepository
from app.modules.teachers.repository import TeacherRepository
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserMutationRequest, UserRead


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_users(self, search: str | None = None, role: str | None = None, sort_dir: str = "desc") -> list[UserRead]:
        users = [self.to_read(user) for user in self.user_repository.find_all_ordered()]
        if validators.has_text(search):
            query = search.strip().lower()
            users = [
                user
                for user in users
                if query in " ".join(
                    [
                        user.login_id or "",
                        user.email or "",
                        user.role or "",
                        user.profile_type or "",
                    ]
                ).lower()
            ]
        if validators.has_text(role):
            normalized_role = role.strip().lower()
            users = [user for user in users if (user.role or "").strip().lower() == normalized_role]
        return users if (sort_dir or "desc").strip().lower() != "asc" else list(reversed(users))

    def get_user(self, user_id: int) -> UserRead:
        return self.to_read(self.find_user(user_id))

    def create_user(self, request: UserMutationRequest) -> UserRead:
        validators.require_text(request.password, "password")
        user = User()
        self.apply_user(user, request, current_user_id=None)
        return self.to_read(self.user_repository.save(user))

    def update_user(self, user_id: int, request: UserMutationRequest) -> UserRead:
        user = self.find_user(user_id)
        self.apply_user(user, request, current_user_id=user.user_id)
        return self.to_read(self.user_repository.save(user))

    def delete_user(self, user_id: int) -> None:
        self.user_repository.delete(self.find_user(user_id))

    def find_user(self, user_id: int | None) -> User:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def apply_user(self, user: User, request: UserMutationRequest, current_user_id: int | None) -> None:
        role = validators.normalize_required_choice(request.role, validators.USER_ROLES, "role")
        login_id = helpers.normalize_code(request.login_id)
        email = helpers.trim_to_none(str(request.email) if request.email is not None else None)
        account_status = (
            validators.normalize_optional_choice(request.account_status, validators.ACCOUNT_STATUSES, "accountStatus")
            or "ACTIVE"
        )

        validators.require_text(login_id, "loginId")
        validators.require_text(email, "email")
        self.validate_profile_links(role, request, current_user_id)
        assert login_id is not None
        assert email is not None

        if self.user_repository.exists_by_login_id(login_id, exclude_user_id=current_user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="loginId already exists")
        if self.user_repository.exists_by_email(email, exclude_user_id=current_user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        user.login_id = login_id
        user.legacy_username = login_id
        user.email = email.lower()
        user.role = role
        user.account_status = account_status
        user.student_id = request.student_id
        user.teacher_id = request.teacher_id
        user.staff_id = request.staff_id
        if validators.has_text(request.password):
            user.password_hash = hash_password(request.password or "")

    def validate_profile_links(self, role: str, request: UserMutationRequest, current_user_id: int | None) -> None:
        normalized_role = role.lower()
        if normalized_role != "student":
            validators.require(request.student_id is None, "studentId can only be linked to Student role")
        else:
            validators.require(request.student_id is not None, "studentId is required for Student role")
            if StudentRepository(self.user_repository.session).find_by_id(request.student_id) is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            if self.user_repository.exists_by_student_id(request.student_id, exclude_user_id=current_user_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student is already linked to another user")

        if normalized_role != "teacher":
            validators.require(request.teacher_id is None, "teacherId can only be linked to Teacher role")
        else:
            validators.require(request.teacher_id is not None, "teacherId is required for Teacher role")
            if TeacherRepository(self.user_repository.session).find_by_id(request.teacher_id) is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
            if self.user_repository.exists_by_teacher_id(request.teacher_id, exclude_user_id=current_user_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher is already linked to another user")

        if normalized_role != "staff":
            validators.require(request.staff_id is None, "staffId can only be linked to Staff role")
        else:
            validators.require(request.staff_id is not None, "staffId is required for Staff role")
            if StaffRepository(self.user_repository.session).find_by_id(request.staff_id) is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
            if self.user_repository.exists_by_staff_id(request.staff_id, exclude_user_id=current_user_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Staff is already linked to another user")

    def to_read(self, user: User) -> UserRead:
        return UserRead(
            user_id=user.user_id,
            login_id=user.login_id,
            username=user.login_id,
            email=user.email,
            role=user.role,
            student_id=user.student_id,
            teacher_id=user.teacher_id,
            staff_id=user.staff_id,
            profile_type=user.profile_type,
            profile_id=user.profile_id,
            account_status=user.account_status,
            registered_at=user.registered_at,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )
