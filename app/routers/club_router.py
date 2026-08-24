from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.club import ClubCreate, ClubResponse, ClubUpdate
from app.services.club import (
    create_club_service,
    get_my_clubs_service,
    get_club_detail_service,
    update_club_put_service,
    update_club_patch_service,
    delete_club_service,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/clubs", tags=["Clubs"])


# Thêm câu lạc bộ
@router.post("/", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(
    data: ClubCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    user_id_str = current_user.get("sub")

    user_id = int(user_id_str)

    return create_club_service(db=db, data=data, user_id=user_id)


# Lấy danh sách câu lạc bộ mà User tham gia
@router.get("/", response_model=List[ClubResponse])
def get_my_clubs(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    return get_my_clubs_service(db=db, user_id=user_id, search=search)


# Lấy thông tin câu lạc bộ theo id mà User tham gia
@router.get("/{club_id}", response_model=ClubResponse, status_code=status.HTTP_200_OK)
def get_club_detail(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    user_id = int(current_user["sub"])

    return get_club_detail_service(db=db, club_id=club_id, user_id=user_id)


# Cập nhật toàn bộ câu lạc bộ
@router.put("/{club_id}", response_model=ClubResponse, status_code=status.HTTP_200_OK)
def update_club_put(
    club_id: int,
    club_in: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    return update_club_put_service(
        db=db, club_id=club_id, club_in=club_in, current_user_id=user_id
    )


# Cập nhật một phần câu lạc bộ
@router.patch("/{club_id}", response_model=ClubResponse, status_code=status.HTTP_200_OK)
def update_club_patch(
    club_id: int,
    club_in: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    return update_club_patch_service(
        db=db, club_id=club_id, club_in=club_in, current_user_id=user_id
    )


# Xóa câu lạc bộ
@router.delete("/{club_id}", status_code=status.HTTP_200_OK)
def delete_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])
    return delete_club_service(db=db, club_id=club_id, current_user_id=user_id)
