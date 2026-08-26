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


def get_current_user_id(current_user: dict):
    raw_id = current_user.get("user_id") or current_user.get("sub")
    return int(raw_id) if raw_id is not None else None


def is_club_owner(db: Session, club_id: int, user_id: int):
    if not user_id:
        return False
    return (
        db.query(ClubModel)
        .filter(ClubModel.club_id == club_id, ClubModel.owner_id == user_id)
        .first()
        is not None
    )


def is_club_member(db: Session, club_id: int, user_id: int) -> bool:
    if not user_id:
        return False
    if is_club_owner(db, club_id, user_id):
        return True
    return (
        db.query(Club_membersModel)
        .filter(
            Club_membersModel.club_id == club_id, Club_membersModel.user_id == user_id
        )
        .first()
        is not None
    )


def validate_status_transition(
    current_status: ActivityStatus, new_status: ActivityStatus
):
    if current_status == new_status:
        return

    valid_transitions = {
        ActivityStatus.TODO: [ActivityStatus.IN_PROGRESS, ActivityStatus.DONE],
        ActivityStatus.IN_PROGRESS: [ActivityStatus.DONE, ActivityStatus.TODO],
        ActivityStatus.DONE: [ActivityStatus.TODO, ActivityStatus.IN_PROGRESS],
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise BadRequestException(
            f"Không thể chuyển trạng thái từ '{current_status}' sang '{new_status}'"
        )


def get_club_activities(
    db: Session,
    club_id: int,
    current_user: dict,
    status_filter: ActivityStatus | None = None,
    priority_filter: ActivityPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    if not db.query(ClubModel).filter(ClubModel.club_id == club_id).first():
        raise NotFoundException(f"Không tìm thấy câu lạc bộ ID = {club_id}")

    user_role = current_user.get("role")
    user_id = get_current_user_id(current_user)

    if user_role != "ADMIN" and not is_club_member(db, club_id, user_id):
        raise ForbiddenException(
            "Bạn không phải thành viên của câu lạc bộ này nên không có quyền xem danh sách hoạt động"
        )

    query = db.query(Club_activitiesModel).filter(
        Club_activitiesModel.club_id == club_id
    )

    if user_role != "ADMIN" and not is_club_owner(db, club_id, user_id):
        query = query.filter(Club_activitiesModel.assignee_id == user_id)
    elif assignee_id:
        query = query.filter(Club_activitiesModel.assignee_id == int(assignee_id))

    if status_filter:
        query = query.filter(Club_activitiesModel.status == status_filter)
    if priority_filter:
        query = query.filter(Club_activitiesModel.priority == priority_filter)
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
    db: Session, club_id: int, activity_id: int, current_user: dict
):
    if not db.query(ClubModel).filter(ClubModel.club_id == club_id).first():
        raise NotFoundException(f"Không tìm thấy câu lạc bộ với ID = {club_id}")

    user_role = current_user.get("role")
    user_id = get_current_user_id(current_user)

    if user_role != "ADMIN" and not is_club_member(db, club_id, user_id):
        raise ForbiddenException(
            "Bạn không phải thành viên của câu lạc bộ này nên không có quyền xem chi tiết hoạt động"
        )

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
            f"Không tìm thấy hoạt động với ID = {activity_id} trong câu lạc bộ này"
        )

    if user_role != "ADMIN" and not is_club_owner(db, club_id, user_id):
        if activity.assignee_id != user_id:
            raise ForbiddenException(
                "Bạn chỉ có quyền xem chi tiết các hoạt động được giao cho chính mình"
            )

    return activity


def create_activity(
    db: Session,
    club_id: int,
    activity_in: ActivityCreate,
    current_user: dict,
):
    if not db.query(ClubModel).filter(ClubModel.club_id == club_id).first():
        raise NotFoundException(f"Không tìm thấy câu lạc bộ ID = {club_id}")

    user_role = current_user.get("role")
    user_id = get_current_user_id(current_user)

    if user_role != "ADMIN" and not is_club_owner(db, club_id, user_id):
        raise ForbiddenException(
            "Chỉ ADMIN hệ thống hoặc Chủ sở hữu (Owner) câu lạc bộ mới có quyền tạo hoạt động"
        )

    if activity_in.assignee_id and not is_club_member(
        db, club_id, int(activity_in.assignee_id)
    ):
        raise BadRequestException(
            "Người được giao nhiệm vụ không phải là thành viên trong câu lạc bộ"
        )

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


def update_activity(
    db: Session,
    club_id: int,
    activity_id: int,
    activity_in: ActivityUpdate,
    current_user: dict,
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
        raise NotFoundException("Không tìm thấy hoạt động trong câu lạc bộ này")

    user_role = current_user.get("role")
    user_id = get_current_user_id(current_user)

    if user_role != "ADMIN" and not is_club_owner(db, club_id, user_id):
        raise ForbiddenException(
            "Chỉ ADMIN hệ thống hoặc Chủ sở hữu (Owner) câu lạc bộ mới có quyền chỉnh sửa hoạt động"
        )

    update_data = activity_in.model_dump(exclude_unset=True)

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        if not is_club_member(db, club_id, int(update_data["assignee_id"])):
            raise BadRequestException(
                "Người được phân công mới không phải là thành viên trong câu lạc bộ"
            )

    if "status" in update_data and update_data["status"] is not None:
        validate_status_transition(activity.status, update_data["status"])

    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(
    db: Session, club_id: int, activity_id: int, current_user: dict
) -> dict:
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
            f"Không tìm thấy hoạt động với ID = {activity_id} trong câu lạc bộ này"
        )

    user_role = current_user.get("role")
    user_id = get_current_user_id(current_user)

    if user_role != "ADMIN" and not is_club_owner(db, club_id, user_id):
        raise ForbiddenException(
            "Chỉ ADMIN hệ thống hoặc Chủ sở hữu (Owner) câu lạc bộ mới có quyền xóa hoạt động"
        )

    db.delete(activity)
    db.commit()

    return {"message": f"Xóa thành công hoạt động với ID = {activity_id}"}
