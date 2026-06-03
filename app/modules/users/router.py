from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import PageResponse, paginate_items
from app.db.session import get_db_session
from app.modules.auth.dependencies import require_roles
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserMutationRequest, UserRead
from app.modules.users.service import UserService


router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[Depends(require_roles("Admin"))])


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(session))


@router.get("", response_model=list[UserRead])
def get_users(
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    user_service: UserService = Depends(get_user_service),
) -> list[UserRead]:
    return user_service.get_users(search=search, role=role, sort_dir=sort_dir)


@router.get("/page", response_model=PageResponse[UserRead])
def get_users_page(
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    sort_dir: str = Query(default="desc", alias="sortDir"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
    user_service: UserService = Depends(get_user_service),
) -> PageResponse[UserRead]:
    return paginate_items(user_service.get_users(search=search, role=role, sort_dir=sort_dir), page, page_size)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, user_service: UserService = Depends(get_user_service)) -> UserRead:
    return user_service.get_user(user_id)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(request: UserMutationRequest, user_service: UserService = Depends(get_user_service)) -> UserRead:
    return user_service.create_user(request)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    request: UserMutationRequest,
    user_service: UserService = Depends(get_user_service),
) -> UserRead:
    return user_service.update_user(user_id, request)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)) -> Response:
    user_service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
