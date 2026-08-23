from sqlalchemy.orm import Session

from app.schemas.user import UserRegister
from app.models.user import UserModel
from app.core.security import hash_password
from app.core.exceptions import BadRequestException


def register_user(data: UserRegister, db: Session) -> UserModel:
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
