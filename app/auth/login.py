from sqlalchemy.orm import Session

from app.schemas.user import UserLogin
from app.models.user import UserModel
from app.models.advanced_models import Refresh_tokensModel
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.core.exceptions import UnauthorizedException


def login_user(data: UserLogin, db: Session) -> str:
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if user is None:
        raise UnauthorizedException("Tài khoản hoặc mật khẩu không chính xác")

    check_pass = verify_password(data.password, user.password_hash)

    if check_pass is False:
        raise UnauthorizedException("Tài khoản hoặc mật khẩu không chính xác")

    access_token = create_access_token(user.user_id, user.role)
    raw_refresh_token, expires_at = create_refresh_token(user_id=user.user_id)

    hashed_refresh_token = hash_token(raw_refresh_token)

    db_token = Refresh_tokensModel(
        token=hashed_refresh_token,
        user_id=user.user_id,
        expires_at=expires_at,
        is_revoked=False,
    )

    db.add(db_token)
    db.commit()

    return access_token, raw_refresh_token
