from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class ActivityStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ActivityPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: ActivityPriority = ActivityPriority.MEDIUM
    status: ActivityStatus = ActivityStatus.TODO
    due_date: Optional[date] = None


class ActivityCreate(ActivityBase):
    assignee_id: int | None = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[ActivityStatus] = None
    priority: Optional[ActivityPriority] = None
    due_date: Optional[date] = None


class ActivityResponse(BaseModel):
    activity_id: int
    club_id: int
    title: str
    description: Optional[str]
    assignee_id: Optional[int]
    created_by: int
    status: ActivityStatus
    priority: ActivityPriority
    due_date: Optional[date]
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class ActivityListResponse(BaseModel):
    total: int
    page: int
    limit: int
    activities: List[ActivityResponse]


# Schema thông tin user cơ bản để lồng vào (Nested Schema)
class UserBasicInfo(BaseModel):
    user_id: int
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# Schema Response chi tiết Activity
class ActivityDetailResponse(BaseModel):
    activity_id: int
    club_id: int
    title: str
    description: Optional[str]
    status: ActivityStatus
    priority: ActivityPriority
    due_date: Optional[date]
    created_at: date

    # ID gốc
    assignee_id: Optional[int]
    created_by: int

    # Thông tin User chi tiết được lồng vào qua Relationship
    assignee: Optional[UserBasicInfo] = None
    creator: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)
