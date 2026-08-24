from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional
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
@router.get("", response_model=list[UserResponse])
def get_all_users(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(role_guard),
):
    query = db.query(UserModel)

    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
    if search:
        query = query.filter(
            or_(UserModel.full_name.contains(search), UserModel.email.contains(search))
        )

    return query.all()
