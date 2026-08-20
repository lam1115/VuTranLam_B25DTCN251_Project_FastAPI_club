from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class CreateUser(UserBase):
    password: str


class UpdateUser(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)
