import os, bcrypt, jwt, hashlib

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


# Băm mật khẩu
def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(plain_password.encode("utf-8"), salt)

    return password_hash.decode("utf-8")


# Kiểm tra mật khẩu
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# Tạo access token
def create_access_token(user_id: str, full_name: str, email: str, role: str) -> str:
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    pay_load = {
        "sub": str(user_id),
        "full_name": full_name,
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire_time,
    }
    token = jwt.encode(pay_load, SECRET_KEY, algorithm=ALGORITHM)

    return token


# Tạo refesh token
def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    expire_time = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": str(user_id), "type": "refresh", "exp": expire_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire_time


# Băm refesh token
def hash_token(token: str) -> str:
    """Băm chuỗi JWT Token thành chuỗi SHA-256 cố định 64 ký tự."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
