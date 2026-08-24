from sqlalchemy.orm import Session
from typing import List
from app.models.club import ClubModel, Club_membersModel
from app.schemas.club import ClubCreate, ClubUpdate
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


# Tạo câu lạc bộ mới
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


# Lấy danh sách câu lạc bộ mà bản thân tham gia
def get_my_clubs_service(
    db: Session, user_id: int, search: str | None = None
) -> List[ClubModel]:
    query = (
        db.query(ClubModel)
        .join(Club_membersModel, ClubModel.club_id == Club_membersModel.club_id)
        .filter(Club_membersModel.user_id == user_id)
    )

    if search:
        query = query.filter(ClubModel.club_name.ilike(f"%{search.strip()}%"))

    return query.all()


# Lây thông tin chi tiết câu lạc bộ mà bản thân tham gia
def get_club_detail_service(db: Session, club_id: int, user_id: int) -> ClubModel:
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại!")

    is_member = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id, Club_membersModel.user_id == user_id
        )
        .first()
    )

    if not is_member:
        raise ForbiddenException(
            "Bạn không phải là thành viên của câu lạc bộ này!",
        )

    return club


def validate_owner(db: Session, club_id: int, current_user_id: int) -> ClubModel:
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại!")

    # 1. Kiểm tra quyền Owner
    if club.owner_id != current_user_id:
        raise ForbiddenException(
            "Chỉ Owner của câu lạc bộ mới có quyền thực hiện thao tác này!",
        )

    return club


def single_member(db: Session, club_id: int, current_user_id: int) -> ClubModel:
    club = validate_owner(db, club_id, current_user_id)

    # Kiểm tra số lượng thành viên trong CLB
    member_count = (
        db.query(Club_membersModel).filter(Club_membersModel.club_id == club_id).count()
    )
    if member_count > 1:
        raise BadRequestException(
            f"Thao tác thất bại! Câu lạc bộ hiện có {member_count} thành viên. Thao tác chỉ cho phép khi câu lạc bộ chỉ còn duy nhất 1 thành viên (Owner).",
        )

    return club


# Cập nhật toàn bộ thông tin câu lạc bộ
def update_club_put_service(
    db: Session, club_id: int, club_in: ClubUpdate, current_user_id: int
) -> ClubModel:
    club = validate_owner(db, club_id, current_user_id)

    # Kiểm tra trùng tên
    if club_in.club_name != club.club_name:
        existing = (
            db.query(ClubModel).filter(ClubModel.club_name == club_in.club_name).first()
        )
        if existing:
            raise BadRequestException("Tên câu lạc bộ đã tồn tại!")

    club.club_name = club_in.club_name
    club.description = club_in.description

    db.commit()
    db.refresh(club)
    return club


# Cập nhật một phần câu lạc bộ
def update_club_patch_service(
    db: Session, club_id: int, club_in: ClubUpdate, current_user_id: int
) -> ClubModel:
    club = validate_owner(db, club_id, current_user_id)

    # Lấy các trường dữ liệu thực sự được client gửi lên
    update_data = club_in.model_dump(exclude_unset=True)

    if "club_name" in update_data and update_data["club_name"] != club.club_name:
        existing = (
            db.query(ClubModel)
            .filter(ClubModel.club_name == update_data["club_name"])
            .first()
        )
        if existing:
            raise BadRequestException("Tên câu lạc bộ đã tồn tại!")

    for key, value in update_data.items():
        setattr(club, key, value)

    db.commit()
    db.refresh(club)
    return club


# Xóa câu lạc bộ
def delete_club_service(db: Session, club_id: int, current_user_id: int) -> dict:
    club = single_member(db, club_id, current_user_id)

    # Xóa bản ghi thành viên Owner duy nhất trước để tránh ràng buộc khóa ngoại
    db.query(Club_membersModel).filter(Club_membersModel.club_id == club_id).delete()

    # Xóa câu lạc bộ
    db.delete(club)
    db.commit()

    return {"message": "Đã xóa câu lạc bộ thành công!"}
