from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    USER = "User"
    ADMIN = "Admin"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class CreateUser(UserBase):
    password: str


class UpdateUser(BaseModel):
    full_name: str
    email: EmailStr


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)
