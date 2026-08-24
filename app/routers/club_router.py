from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.club import ClubCreate, ClubResponse
from app.services.club import create_club_service, get_my_clubs_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.post("/", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(
    data: ClubCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    user_id_str = current_user.get("sub")

    user_id = int(user_id_str)

    return create_club_service(db=db, data=data, user_id=user_id)


@router.get("/me", response_model=List[ClubResponse])
def get_my_clubs(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    return get_my_clubs_service(db=db, user_id=user_id, search=search)
