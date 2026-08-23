from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.club import ClubCreate, ClubResponse
from app.services.club import create_club_service
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
