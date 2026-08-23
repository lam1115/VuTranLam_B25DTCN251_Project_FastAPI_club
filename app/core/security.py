import os, bcrypt, jwt, hashlib

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(plain_password.encode("utf-8"), salt)

    return password_hash.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(user_id: str, role: str) -> str:
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    pay_load = {"sub": str(user_id), "role": role, "type": "access", "exp": expire_time}
    token = jwt.encode(pay_load, SECRET_KEY, algorithm=ALGORITHM)

    return token


def create_refresh_token(user_id: int):
    expire_time = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": str(user_id), "type": "refresh", "exp": expire_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire_time


def hash_token(token: str) -> str:
    """Băm chuỗi JWT Token thành chuỗi SHA-256 cố định 64 ký tự."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
