from sqlalchemy.orm import Session
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
