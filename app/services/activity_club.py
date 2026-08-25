from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models import ClubModel, Club_membersModel, Club_activitiesModel, UserModel
from app.schemas.club_activity import (
    ActivityCreate,
    ActivityStatus,
    ActivityPriority,
    ActivityUpdate,
)
from app.core.exceptions import (
    ForbiddenException,
    BadRequestException,
    NotFoundException,
)


def validate_club_member(db: Session, club_id: int, user_id: int) -> bool:
    """
    Kiểm tra User có quyền thành viên trong CLB không.
    Hợp lệ nếu: User là Người tạo CLB OR User nằm trong bảng Club_members.
    """
    # 1. Kiểm tra User có phải là Người tạo/Chủ sở hữu của CLB không
    # (Lưu ý: Thay `created_by` hoặc `owner_id` đúng theo tên trường trong ClubModel của bạn)
    club = (
        db.query(ClubModel)
        .filter(
            ClubModel.club_id == club_id,
            ClubModel.created_by == user_id,  # Hoặc ClubModel.owner_id == user_id
        )
        .first()
    )

    if club:
        return True

    # 2. Kiểm tra User có nằm trong bảng thành viên CLB không
    is_member = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id, Club_membersModel.user_id == user_id
        )
        .first()
        is not None
    )

    return is_member


def validate_status_transition(
    current_status: ActivityStatus, new_status: ActivityStatus
):
    """Kiểm tra logic luồng chuyển trạng thái (Workflow)."""
    if current_status == new_status:
        return

    # Quy tắc workflow: TODO -> IN_PROGRESS -> DONE (hoặc reset về TODO)
    valid_transitions = {
        ActivityStatus.TODO: [ActivityStatus.IN_PROGRESS, ActivityStatus.DONE],
        ActivityStatus.IN_PROGRESS: [ActivityStatus.DONE, ActivityStatus.TODO],
        ActivityStatus.DONE: [ActivityStatus.TODO, ActivityStatus.IN_PROGRESS],
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise BadRequestException(
            f"Không thể chuyển trạng thái từ '{current_status}' sang '{new_status}'",
        )


def create_activity(
    db: Session,
    club_id: int,
    activity_in: ActivityCreate,
    current_user: dict,  # Nhận current_user dạng dict
):
    # 1. Kiểm tra CLB tồn tại
    if not db.query(ClubModel).filter(ClubModel.club_id == club_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy câu lạc bộ ID = {club_id}",
        )

    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    # 2. Kiểm tra quyền tạo: ADMIN hoặc Thành viên trong CLB
    if user_role != "ADMIN" and not validate_club_member(db, club_id, user_id):
        raise ForbiddenException(
            "Bạn không phải thành viên của câu lạc bộ này nên không có quyền tạo hoạt động",
        )

    # 3. Validate assignee_id (nếu gán task): Phải là thành viên trong CLB
    if activity_in.assignee_id and not validate_club_member(
        db, club_id, activity_in.assignee_id
    ):
        raise BadRequestException(
            "Người được giao nhiệm vụ không phải là thành viên trong câu lạc bộ",
        )

    # 4. Lưu vào DB
    new_activity = Club_activitiesModel(
        club_id=club_id,
        title=activity_in.title,
        description=activity_in.description,
        assignee_id=activity_in.assignee_id,
        created_by=user_id,
        status=activity_in.status,
        priority=activity_in.priority,
        due_date=activity_in.due_date,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


def get_club_activities(
    db: Session,
    club_id: int,
    current_user: dict,  # Nhận current_user dạng dict
    status_filter: ActivityStatus | None = None,
    priority_filter: ActivityPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    # 1. Kiểm tra CLB tồn tại
    if not db.query(ClubModel).filter(ClubModel.club_id == club_id).first():
        raise NotFoundException(
            f"Không tìm thấy câu lạc bộ ID = {club_id}",
        )

    user_role = current_user.get("role")
    user_id = current_user.get("user_id")

    # 2. Kiểm tra quyền: Phải là ADMIN hoặc là Thành viên trong CLB
    if user_role != "ADMIN" and not validate_club_member(db, club_id, user_id):
        raise ForbiddenException(
            "Bạn không phải thành viên của câu lạc bộ này nên không có quyền xem danh sách hoạt động",
        )

    # 3. Query & Bộ lọc
    query = db.query(Club_activitiesModel).filter(
        Club_activitiesModel.club_id == club_id
    )

    if status_filter:
        query = query.filter(Club_activitiesModel.status == status_filter)
    if priority_filter:
        query = query.filter(Club_activitiesModel.priority == priority_filter)
    if assignee_id:
        query = query.filter(Club_activitiesModel.assignee_id == assignee_id)
    if search:
        query = query.filter(Club_activitiesModel.title.ilike(f"%{search.strip()}%"))

    total = query.count()
    skip = (page - 1) * limit
    activities = (
        query.order_by(Club_activitiesModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"total": total, "page": page, "limit": limit, "activities": activities}


def get_activity_detail(
    db: Session, club_id: int, activity_id: int, current_user: UserModel
):
    # 1. Kiểm tra Câu lạc bộ có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException(
            f"Không tìm thấy câu lạc bộ với ID = {club_id}",
        )

    # 2. Kiểm tra phân quyền: User phải là thành viên CLB (MEMBER/OWNER) hoặc ADMIN
    if current_user.get("role") != "ADMIN":
        member_record = (
            db.query(Club_membersModel)
            .filter(
                Club_membersModel.club_id == club_id,
                Club_membersModel.user_id == current_user.get("user_id"),
            )
            .first()
        )

        if not member_record:
            raise ForbiddenException(
                "Bạn không phải thành viên của câu lạc bộ này nên không có quyền xem chi tiết hoạt động",
            )

    # 3. Lấy thông tin Activity và đảm bảo nó thuộc về CLB được chỉ định
    # Tính năng Lazy Loading / Joined Loading của SQLAlchemy sẽ tự động query các Relationship
    # ("creator" và "assignee") vì chúng ta đã khai báo trong Model và map bằng Pydantic.
    activity = (
        db.query(Club_activitiesModel)
        .filter(
            Club_activitiesModel.activity_id == activity_id,
            Club_activitiesModel.club_id == club_id,
        )
        .first()
    )

    if not activity:
        raise NotFoundException(
            f"Không tìm thấy hoạt động với ID = {activity_id} trong câu lạc bộ này",
        )

    return activity


def update_activity(
    db: Session,
    club_id: int,
    activity_id: int,
    activity_in: ActivityUpdate,
    current_user: UserModel,
):
    activity = (
        db.query(Club_activitiesModel)
        .filter(
            Club_activitiesModel.activity_id == activity_id,
            Club_activitiesModel.club_id == club_id,
        )
        .first()
    )
    if not activity:
        raise NotFoundException("Không tìm thấy hoạt động")

    member_record = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id,
            Club_membersModel.user_id == current_user.get("user_id"),
        )
        .first()
    )

    is_system_admin = current_user.get("role") == "ADMIN"
    is_club_manager = member_record and member_record.role in [
        "OWNER",
        "LEADER",
        "ADMIN",
    ]
    is_creator = activity.created_by == current_user.user_id
    is_assignee = activity.assignee_id == current_user.user_id

    if not (is_system_admin or is_club_manager or is_creator or is_assignee):
        raise ForbiddenException(
            "Bạn không có quyền chỉnh sửa hoạt động này",
        )

    update_data = activity_in.model_dump(exclude_unset=True)

    # Assignee chỉ được cập nhật status
    if is_assignee and not (is_system_admin or is_club_manager or is_creator):
        if set(update_data.keys()) - {"status"}:
            raise ForbiddenException(
                "Người thực hiện chỉ có quyền cập nhật trạng thái (status)",
            )

    # Phân việc: Validate assignee mới thuộc CLB
    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        if not validate_club_member(db, club_id, update_data["assignee_id"]):
            raise BadRequestException(
                "Người được phân công mới không phải là thành viên trong câu lạc bộ",
            )

    # Workflow Validation cho Status
    if "status" in update_data:
        validate_status_transition(activity.status, update_data["status"])

    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(
    db: Session, club_id: int, activity_id: int, current_user: UserModel
) -> dict:
    # 1. Kiểm tra Câu lạc bộ có tồn tại không
    club = db.query(ClubModel).filter(ClubModel.club_id == club_id).first()
    if not club:
        raise NotFoundException(
            f"Không tìm thấy câu lạc bộ với ID = {club_id}",
        )

    # 2. Kiểm tra Hoạt động có tồn tại trong CLB không
    activity = (
        db.query(Club_activitiesModel)
        .filter(
            Club_activitiesModel.activity_id == activity_id,
            Club_activitiesModel.club_id == club_id,
        )
        .first()
    )

    if not activity:
        raise NotFoundException(
            f"Không tìm thấy hoạt động với ID = {activity_id} trong câu lạc bộ này",
        )

    # 3. Kiểm tra tư cách thành viên trong CLB
    member_record = (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id,
            Club_membersModel.user_id == current_user.get("user_id"),
        )
        .first()
    )

    if current_user.get("role") != "ADMIN" and not member_record:
        raise ForbiddenException(
            "Bạn không phải thành viên của câu lạc bộ này",
        )

    # 4. Kiểm tra phân quyền xóa (Permission Logic)
    # Chỉ cho phép: System ADMIN, Ban quản lý CLB (OWNER/LEADER/ADMIN), hoặc Người tạo task
    is_system_admin = current_user.role == "ADMIN"
    is_club_manager = member_record and member_record.role in [
        "OWNER",
        "LEADER",
        "ADMIN",
    ]
    is_creator = activity.created_by == current_user.user_id

    if not (is_system_admin or is_club_manager or is_creator):
        raise ForbiddenException(
            "Bạn không có quyền xóa hoạt động này. Chỉ người tạo hoặc Ban quản trị mới có quyền xóa.",
        )

    # 5. Xóa khỏi Database
    db.delete(activity)
    db.commit()

    return {"message": f"Xóa thành công hoạt động với ID = {activity_id}"}
