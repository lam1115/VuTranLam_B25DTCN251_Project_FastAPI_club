from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies import get_db
from app.models.user import UserModel
from app.models.advanced_models import Refresh_tokensModel
from app.schemas.user import UserRegister, UserLogin, TokenResponse, RefreshTokenSchema
from app.auth.register import register_user
from app.auth.login import login_user
from app.core.exceptions import UnauthorizedException
from app.core.security import hash_token, create_access_token
from app.dependencies import verify_refresh_token

router = APIRouter(prefix="/api/studentclub/auth", tags=["Authentication User"])


@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)) -> dict:
    user = register_user(data, db)

    return {
        "message": "Đăng ký tài khoản thành công",
        "username": user.full_name,
        "role": user.role,
    }


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)) -> dict:
    access_token, raw_refresh_token = login_user(data, db)

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token(
    body: RefreshTokenSchema,
    payload: dict = Depends(
        verify_refresh_token
    ),  # Tự động verify JWT và type='refresh'
    db: Session = Depends(get_db),
):
    # 1. BĂM chuỗi token gốc từ Body (body.refresh_token)
    hashed_incoming_token = hash_token(body.refresh_token)

    # 2. Truy vấn trong DB
    db_token = (
        db.query(Refresh_tokensModel)
        .filter(Refresh_tokensModel.token == hashed_incoming_token)
        .first()
    )

    # 3. Kiểm tra điều kiện hợp lệ trong DB
    if not db_token:
        raise UnauthorizedException("Refresh token không tồn tại")

    if db_token.is_revoked:
        raise UnauthorizedException("Refresh token đã bị thu hồi (vô hiệu hóa)")

    if db_token.expires_at < datetime.now():
        raise UnauthorizedException("Refresh token đã hết hạn")

    # 4. Lấy thông tin user và cấp Access Token MỚI
    user = db.query(UserModel).filter(UserModel.user_id == db_token.user_id).first()
    new_access_token = create_access_token(user_id=user.user_id, role=user.role)

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(body: RefreshTokenSchema, db: Session = Depends(get_db)):
    # Băm token gửi lên từ Body
    hashed_incoming_token = hash_token(body.refresh_token)

    # Tìm trong DB và đánh dấu is_revoked = True
    db_token = (
        db.query(Refresh_tokensModel)
        .filter(Refresh_tokensModel.token == hashed_incoming_token)
        .first()
    )

    if db_token:
        db_token.is_revoked = True
        db.commit()

    return {"message": "Đăng xuất thành công"}
