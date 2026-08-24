import os, jwt
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.database import SessionLocal
from app.core.exceptions import ForbiddenException
from app.schemas.user import RefreshTokenSchema
from app.core.exceptions import UnauthorizedException

security = HTTPBearer()
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def decode_token(token: str) -> dict:
    """Hàm lõi chuyên giải mã và kiểm tra token chung."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Token không hợp lệ")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    payload = decode_token(credentials.credentials)  # Dùng lại helper

    # Kiểm tra đảm bảo đây là Access Token
    if payload.get("type") != "access":
        raise UnauthorizedException("Vui lòng sử dụng Access Token")

    return payload


def verify_refresh_token(body: RefreshTokenSchema) -> dict:
    payload = decode_token(body.refresh_token)  # Dùng lại helper

    # Kiểm tra đảm bảo đây là Refresh Token
    if payload.get("type") != "refresh":
        raise UnauthorizedException("Vui lòng sử dụng Refresh Token")

    return payload


def role_guard(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "ADMIN":
        raise ForbiddenException("Quyền truy cập bị từ trối. Yêu cầu vai trò ADMIN")
