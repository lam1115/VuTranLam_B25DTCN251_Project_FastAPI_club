from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
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
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_name: Optional[str] = Field(
        default=None, validation_alias="assignee.full_name"
    )
    status: ActivityStatus
    priority: ActivityPriority
    due_date: Optional[datetime] = None


class ActivityResponse(ActivityBase):
    activity_id: int
    club_name: str = Field(validation_alias="club.club_name")
    assignee_name: Optional[str] = Field(
        default=None, validation_alias="assignee.full_name"
    )
    status: Optional[ActivityStatus] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
