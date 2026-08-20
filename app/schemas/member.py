from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MemberRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class ClubMemberCreate(BaseModel):
    user_id: int
    role: str


class MemberInfo(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class ClubMemberResponse(BaseModel):
    club_name: str = Field(validation_alias="club.club_name")
    user: MemberInfo
    role: MemberRole
    joined_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
