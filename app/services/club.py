from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.club import ClubModel, Club_membersModel
from app.schemas.club import ClubCreate, ClubUpdate
from app.services.activity_log import create_activity_log
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


# Tạo câu lạc bộ mới
def create_club_service(db: Session, data: ClubCreate, user_id: int) -> ClubModel:
    existing_club = (
        db.query(ClubModel)
        .filter(ClubModel.club_name == data.club_name, ClubModel.is_deleted == False)
        .first()
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

    create_activity_log(
        db=db,
        user_id=user_id,
        action="CREATE_CLUB",
        entity_type="CLUB",
        entity_id=new_club.club_id,
        details=f"Đã tạo câu lạc bộ mới '{new_club.club_name}'",
    )

    db.commit()
    db.refresh(new_club)

    return new_club


# Lấy danh sách câu lạc bộ mà bản thân tham gia (Lọc bỏ các CLB đã xóa mềm)
def get_my_clubs_service(
    db: Session, user_id: int, search: str | None = None
) -> List[ClubModel]:
    query = (
        db.query(ClubModel)
        .join(Club_membersModel, ClubModel.club_id == Club_membersModel.club_id)
        .filter(Club_membersModel.user_id == user_id, ClubModel.is_deleted == False)
    )

    if search:
        query = query.filter(ClubModel.club_name.ilike(f"%{search.strip()}%"))

    return query.all()


# Lấy thông tin chi tiết câu lạc bộ mà bản thân tham gia
def get_club_detail_service(db: Session, club_id: int, user_id: int) -> ClubModel:
    club = (
        db.query(ClubModel)
        .filter(ClubModel.club_id == club_id, ClubModel.is_deleted == False)
        .first()
    )
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại hoặc đã bị xóa!")

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
    club = (
        db.query(ClubModel)
        .filter(ClubModel.club_id == club_id, ClubModel.is_deleted == False)
        .first()
    )
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại hoặc đã bị xóa!")

    # 1. Kiểm tra quyền Owner
    if club.owner_id != current_user_id:
        raise ForbiddenException(
            "Chỉ Owner của câu lạc bộ mới có quyền thực hiện thao tác này!",
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
            db.query(ClubModel)
            .filter(
                ClubModel.club_name == club_in.club_name, ClubModel.is_deleted == False
            )
            .first()
        )
        if existing:
            raise BadRequestException("Tên câu lạc bộ đã tồn tại!")

    club.club_name = club_in.club_name
    club.description = club_in.description

    create_activity_log(
        db=db,
        user_id=current_user_id,
        action="UPDATE_CLUB",
        entity_type="CLUB",
        entity_id=club_id,
        details=f"Cập nhật thông tin câu lạc bộ '{club.club_name}'",
    )

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
            .filter(
                ClubModel.club_name == update_data["club_name"],
                ClubModel.is_deleted == False,
            )
            .first()
        )
        if existing:
            raise BadRequestException("Tên câu lạc bộ đã tồn tại!")

    for key, value in update_data.items():
        setattr(club, key, value)

    create_activity_log(
        db=db,
        user_id=current_user_id,
        action="UPDATE_CLUB",
        entity_type="CLUB",
        entity_id=club_id,
        details=f"Cập nhật thông tin câu lạc bộ '{club.club_name}'",
    )

    db.commit()
    db.refresh(club)
    return club


# Xóa mềm câu lạc bộ (Soft Delete)
def delete_club_service(db: Session, club_id: int, current_user_id: int) -> dict:
    club = validate_owner(db, club_id, current_user_id)

    # Đánh dấu đã xóa mềm
    club.is_deleted = True
    club.deleted_at = datetime.now()

    create_activity_log(
        db=db,
        user_id=current_user_id,
        action="DELETE_CLUB",
        entity_type="CLUB",
        entity_id=club_id,
        details=f"Xóa mềm câu lạc bộ '{club.club_name}' (chuyển vào thùng rác)",
    )

    db.commit()

    return {"message": "Đã chuyển câu lạc bộ vào thùng rác thành công!"}


# Khôi phục câu lạc bộ từ thùng rác (Restore)
def restore_club_service(db: Session, club_id: int, current_user_id: int) -> dict:
    # Tìm CLB bị xóa mềm mà người gọi là Owner
    club = (
        db.query(ClubModel)
        .filter(
            ClubModel.club_id == club_id,
            ClubModel.owner_id == current_user_id,
            ClubModel.is_deleted == True,
        )
        .first()
    )
    if not club:
        raise NotFoundException("Không tìm thấy câu lạc bộ trong thùng rác!")

    club.is_deleted = False
    club.deleted_at = None

    create_activity_log(
        db=db,
        user_id=current_user_id,
        action="RESTORE_CLUB",
        entity_type="CLUB",
        entity_id=club_id,
        details=f"Khôi phục câu lạc bộ '{club.club_name}' từ thùng rác",
    )

    db.commit()

    return {"message": "Đã khôi phục câu lạc bộ thành công!"}
