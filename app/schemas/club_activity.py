from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
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
    title: str
    description: Optional[str] = None
    priority: ActivityPriority = ActivityPriority.MEDIUM
    due_date: Optional[datetime] = None


class ActivityCreate(ActivityBase):
    assignee_id: int


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[ActivityStatus] = None
    priority: Optional[ActivityPriority] = None
    due_date: Optional[datetime] = None


class ActivityResponse(BaseModel):
    activity_id: int
    club_id: int
    title: str
    description: Optional[str]
    assignee_id: Optional[int]
    created_by: int
    status: ActivityStatus
    priority: ActivityPriority
    due_date: Optional[datetime]
    created_at: datetime

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

    class Config:
        from_attributes = True


# Schema Response chi tiết Activity (kế thừa từ ActivityResponse cơ bản)
class ActivityDetailResponse(BaseModel):
    activity_id: int
    club_id: int
    title: str
    description: Optional[str]
    status: ActivityStatus
    priority: ActivityPriority
    due_date: Optional[datetime]
    created_at: datetime

    # ID gốc
    assignee_id: Optional[int]
    created_by: int

    # Thông tin User chi tiết được lồng vào (nested) qua Relationship của SQLAlchemy
    assignee: Optional[UserBasicInfo] = None
    creator: UserBasicInfo

    class Config:
        from_attributes = True
