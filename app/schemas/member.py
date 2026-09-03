from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import date
from enum import Enum


class MemberRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class ClubMemberCreate(BaseModel):
    user_id: int


class MemberInfo(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class ClubMemberRemoveRequest(BaseModel):
    new_owner_id: Optional[int] = None


class ClubMemberResponse(BaseModel):
    user: MemberInfo
    role: MemberRole
    joined_at: date

    model_config = ConfigDict(from_attributes=True)
