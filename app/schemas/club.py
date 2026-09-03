from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional

from app.schemas.member import ClubMemberResponse


class ClubBase(BaseModel):
    club_name: str
    description: Optional[str] = None


class OwnerInfo(BaseModel):
    user_id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    club_name: str
    description: Optional[str] = None


class ClubResponse(ClubBase):
    club_id: int
    owner: OwnerInfo
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class ClubDetailResponse(ClubBase):
    club_id: int
    owner: OwnerInfo
    created_at: date
    members: List[ClubMemberResponse] | None = None

    model_config = ConfigDict(from_attributes=True)
