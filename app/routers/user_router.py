from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, role_guard
from app.schemas.user import UserResponse
from app.models.user import UserModel
from app.dependencies import get_db

router = APIRouter(prefix="/api/studentclub/users", tags=["Get User"])


# Lấy thông tin tài khoản bản thân
@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


# Lây thông tin tất cả User, có thêm chức năng search (chỉ hữu hiệu với ADMIN)
@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(
    full_name: str | None = None,
    email: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(role_guard),
):
    query = db.query(UserModel)

    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)

    if full_name and full_name.strip():
        query = query.filter(UserModel.full_name.ilike(f"%{full_name.strip()}%"))

    if email and email.strip():
        query = query.filter(UserModel.email.ilike(f"%{email.strip()}%"))

    return query.all()
