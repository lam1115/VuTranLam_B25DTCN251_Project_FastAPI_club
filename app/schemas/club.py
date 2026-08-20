from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from app.schemas.member import ClubMemberResponse


class ClubBase(BaseModel):
    name: str
    description: Optional[str] = None


class OwnerInfo(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    name: str
    description: str


class ClubResponse(ClubBase):
    id: int
    owner: OwnerInfo
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ClubDetailResponse(ClubBase):
    id: int
    owner: OwnerInfo
    created_at: str
    members: List[ClubMemberResponse] | None = None

    model_config = ConfigDict(from_attributes=True)
