from typing import List

from sqlalchemy.orm import Session, joinedload
from app.models.club import ClubModel, Club_membersModel
from app.models.user import UserModel
from app.schemas.member import ClubMemberCreate
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    BadRequestException,
)


# Thêm thành viên cho câu lạc bộ
def add_club_member_service(
    db: Session, club_id: int, member_in: ClubMemberCreate, current_user_id: int
) -> Club_membersModel:
    # 1. Kiểm tra câu lạc bộ có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại!")

    # 2. Kiểm tra người thực hiện có phải là OWNER không
    if club.owner_id != current_user_id:
        raise ForbiddenException(
            "Chỉ Owner của câu lạc bộ mới có quyền thêm thành viên!",
        )

    # 3. Kiểm tra User được thêm có tồn tại trong hệ thống không
    target_user = (
        db.query(UserModel).filter(UserModel.user_id == member_in.user_id).first()
    )
    if not target_user:
        raise NotFoundException(
            "Người dùng muốn thêm không tồn tại trên hệ thống!",
        )

    # 4. Kiểm tra User đã nằm trong CLB chưa
    existing_member = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id,
            Club_membersModel.user_id == member_in.user_id,
        )
        .first()
    )

    if existing_member:
        raise BadRequestException(
            "Người dùng này đã là thành viên của câu lạc bộ!",
        )

    # 5. Thêm thành viên mới với role mặc định là MEMBER
    new_member = Club_membersModel(
        club_id=club_id, user_id=member_in.user_id, role="MEMBER"
    )
    db.add(new_member)
    db.commit()

    # 6. Truy vấn lại bản ghi kèm theo relationship 'club' (và 'user' nếu schema yêu cầu)
    added_member = (
        db.query(Club_membersModel)
        .options(joinedload(Club_membersModel.club))  # Nạp thông tin club cho schema
        .filter(
            Club_membersModel.club_id == club_id,
            Club_membersModel.user_id == member_in.user_id,
        )
        .first()
    )

    return added_member


# Xóa thành viên câu lạc bộ
def remove_club_member_service(
    db: Session,
    club_id: int,
    target_user_id: int,
    current_user_id: int,
    new_owner_id: int | None = None,
) -> dict:
    # 1. Kiểm tra câu lạc bộ có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại!")

    # 2. Phân quyền: Ai được phép xóa?
    # - Owner có quyền xóa bất kỳ thành viên nào (trừ chính mình nếu chưa chuyển quyền).
    # - Thành viên bình thường chỉ có thể tự xóa chính mình (rời nhóm).
    is_owner_action = club.owner_id == current_user_id
    is_self_removal = current_user_id == target_user_id

    if not is_owner_action and not is_self_removal:
        raise ForbiddenException(
            "Chỉ chủ câu lạc bộ mới có quyền xóa thành viên!",
        )

    # 3. Kiểm tra thành viên cần xóa có tồn tại trong CLB không
    target_member = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id,
            Club_membersModel.user_id == target_user_id,
        )
        .first()
    )

    if not target_member:
        raise NotFoundException(
            "Thành viên cần xóa không nằm trong câu lạc bộ này!",
        )

    # 4. XỬ LÝ LƯU Ý QUAN TRỌNG: Nếu người bị xóa chính là Owner (Owner tự rời nhóm hoặc tự xóa bản thân)
    if target_member.role == "OWNER" or club.owner_id == target_user_id:
        # Kiểm tra tổng số thành viên trong CLB
        total_members = (
            db.query(Club_membersModel)
            .filter(Club_membersModel.club_id == club_id)
            .count()
        )

        if total_members > 1:
            if not new_owner_id:
                raise BadRequestException(
                    "Owner không thể tự xóa/rời khỏi câu lạc bộ khi còn thành viên khác. Bạn bắt buộc phải chỉ định một thành viên khác làm Owner mới (new_owner_id)!",
                )

            if new_owner_id == target_user_id:
                raise BadRequestException(
                    "Owner mới không thể trùng với người đang rời đi!",
                )

            # Kiểm tra xem new_owner_id có thực sự là thành viên trong CLB không
            new_owner_member = (
                db.query(Club_membersModel)
                .filter(
                    Club_membersModel.club_id == club_id,
                    Club_membersModel.user_id == new_owner_id,
                )
                .first()
            )

            if not new_owner_member:
                raise NotFoundException(
                    "Thành viên được chỉ định làm Owner mới không nằm trong câu lạc bộ!",
                )

            # Chuyển giao quyền Owner
            new_owner_member.role = "OWNER"
            club.owner_id = new_owner_id
        else:
            # Bắt buộc Owner xóa toàn bộ CLB nếu chỉ còn 1 mình
            raise BadRequestException(
                "Bạn là thành viên cuối cùng (Owner). Để rời câu lạc bộ này, vui lòng sử dụng chức năng Xóa câu lạc bộ!",
            )

    # 5. Tiến hành xóa thành viên khỏi bảng Club_members
    db.delete(target_member)
    db.commit()

    return {"message": "Đã xóa thành viên khỏi câu lạc bộ thành công!"}


# Trả danh sách member và role
def get_club_members_service(
    db: Session, club_id: int, current_user_id: int
) -> List[Club_membersModel]:
    # 1. Kiểm tra câu lạc bộ có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException("Câu lạc bộ không tồn tại!")

    # 2. Kiểm tra xem người yêu cầu có phải thành viên của CLB không
    is_member = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id,
            Club_membersModel.user_id == current_user_id,
        )
        .first()
    )

    if not is_member:
        raise ForbiddenException(
            "Bạn không phải thành viên của câu lạc bộ này!",
        )

    # 3. Lấy danh sách thành viên kèm thông tin user
    members = (
        db.query(Club_membersModel)
        .options(joinedload(Club_membersModel.user))
        .filter(Club_membersModel.club_id == club_id)
        .all()
    )

    return members
