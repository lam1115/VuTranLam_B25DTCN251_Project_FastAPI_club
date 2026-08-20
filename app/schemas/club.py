from pydantic import BaseModel, ConfigDict


class ClubBase(BaseModel):
    name: str
    description: str


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    name: str
    description: str


class ClubResponse(ClubBase):
    id: int
    owner_id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)
