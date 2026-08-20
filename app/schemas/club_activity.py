from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
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
    due_date: Optional[str] = None


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
    due_date: str


class ActivityResponse(ActivityBase):
    id: int
    club_name: str = Field(validation_alias="club.club_name")
    assignee_name: Optional[str] = Field(
        default=None, validation_alias="assignee.full_name"
    )
    status: ActivityStatus
    created_at: str

    model_config = ConfigDict(from_attributes=True)
