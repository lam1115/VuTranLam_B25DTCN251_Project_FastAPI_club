import re
from sqlalchemy.orm import Session

from app.schemas.user import UserRegister
from app.models.user import UserModel
from app.core.security import hash_password
from app.core.exceptions import BadRequestException


# Đăng ký
def is_strong_password(password: str) -> bool:
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).+$"
    return bool(re.match(pattern, password))


# Đăng ký
def register_user(data: UserRegister, db: Session) -> UserModel:
    # Validate độ mạnh mật khẩu
    if not is_strong_password(data.password):
        raise BadRequestException(
            "Mật khẩu phải bao gồm đầy đủ: chữ in hoa, chữ thường, chữ số và ký tự đặc biệt"
        )

    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if user is not None:
        raise BadRequestException("Email đã tồn tại")

    hash_pass = hash_password(data.password)

    new_user = UserModel(
        email=data.email, password_hash=hash_pass, full_name=data.full_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
