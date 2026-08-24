from sqlalchemy.orm import Session
from typing import Optional
from app.models.club import ClubModel, Club_membersModel
from app.schemas.club import ClubCreate
from app.core.exceptions import BadRequestException


def create_club_service(db: Session, data: ClubCreate, user_id: int) -> ClubModel:
    existing_club = (
        db.query(ClubModel).filter(ClubModel.club_name == data.club_name).first()
    )
    if existing_club:
        raise BadRequestException("Tên câu lạc bộ đã tồn tại!")

    new_club = ClubModel(
        club_name=data.club_name, description=data.description, owner_id=user_id
    )
    db.add(new_club)
    db.flush()

    new_member = Club_membersModel(
        club_id=new_club.club_id, user_id=user_id, role="OWNER"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_club)

    return new_club


def get_my_clubs_service(db: Session, user_id: int, search: str | None = None):
    query = (
        db.query(ClubModel)
        .join(Club_membersModel, ClubModel.club_id == Club_membersModel.club_id)
        .filter(Club_membersModel.user_id == user_id)
    )

    if search:
        query = query.filter(ClubModel.club_name.ilike(f"%{search.strip()}%"))

    return query.all()
