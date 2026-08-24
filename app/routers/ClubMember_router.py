from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.member import (
    ClubMemberCreate,
    ClubMemberResponse,
    ClubMemberRemoveRequest,
)
from app.services.club_member import (
    add_club_member_service,
    remove_club_member_service,
    get_club_members_service,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/clubs", tags=["Club Members"])


# Thêm thành viên cho câu lạc bộ
@router.post(
    "/{club_id}/members",
    response_model=ClubMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_club_member(
    club_id: int,
    member_in: ClubMemberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Lấy user_id của người thực hiện yêu cầu từ token ("sub")
    current_user_id = int(current_user["sub"])

    return add_club_member_service(
        db=db, club_id=club_id, member_in=member_in, current_user_id=current_user_id
    )


# Xóa thành viên ra khỏi câu lạc bộ
@router.delete("/{club_id}/members/{target_user_id}", status_code=status.HTTP_200_OK)
def remove_club_member(
    club_id: int,
    target_user_id: int,
    body: ClubMemberRemoveRequest = Body(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = int(current_user["sub"])
    new_owner_id = body.new_owner_id if body else None

    return remove_club_member_service(
        db=db,
        club_id=club_id,
        target_user_id=target_user_id,
        current_user_id=current_user_id,
        new_owner_id=new_owner_id,
    )


# Lấy danh sách thành viên và role
@router.get(
    "/{club_id}/members",
    response_model=list[ClubMemberResponse],
    status_code=status.HTTP_200_OK,
)
def get_club_members(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = int(current_user["sub"])
    return get_club_members_service(
        db=db, club_id=club_id, current_user_id=current_user_id
    )
