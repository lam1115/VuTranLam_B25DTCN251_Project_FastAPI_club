from pydantic import BaseModel, ConfigDict
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
    description: str
    priority: ActivityPriority
    due_date: str


class ActivityCreate(ActivityBase):
    assignee_id: int


class ActivityUpdate(BaseModel):
    title: str
    description: str
    assignee_id: int
    status: ActivityStatus
    priority: ActivityPriority
    due_date: str


class ActivityResponse(ActivityBase):
    id: int
    club_id: int
    assignee_id: int
    status: ActivityStatus
    created_at: str

    model_config = ConfigDict(from_attributes=True)
