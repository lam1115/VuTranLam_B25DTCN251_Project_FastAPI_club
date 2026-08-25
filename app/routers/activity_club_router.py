from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import UserModel
from app.schemas.club_activity import (
    ActivityCreate,
    ActivityResponse,
    ActivityListResponse,
    ActivityStatus,
    ActivityPriority,
    ActivityDetailResponse,
    ActivityUpdate,
)
from app.services.activity_club import (
    create_activity,
    get_club_activities,
    get_activity_detail,
    update_activity,
    delete_activity,
)

router = APIRouter(prefix="/clubs", tags=["Club Activities"])


@router.post(
    "/{club_id}/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity_endpoint(
    club_id: int,
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return create_activity(
        db=db, club_id=club_id, activity_in=activity_in, current_user=current_user
    )


@router.get("/{club_id}/activities", response_model=ActivityListResponse)
def get_activities_endpoint(
    club_id: int,
    status_filter: ActivityStatus | None = None,
    priority_filter: ActivityPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_club_activities(
        db=db,
        club_id=club_id,
        current_user=current_user,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assignee_id=assignee_id,
        search=search,
        page=page,
        limit=limit,
    )


@router.get(
    "/{club_id}/activities/{activity_id}",
    response_model=ActivityDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_club_activity_detail_endpoint(
    club_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_activity_detail(
        db=db, club_id=club_id, activity_id=activity_id, current_user=current_user
    )


@router.patch("/{club_id}/activities/{activity_id}", response_model=ActivityResponse)
def update_activity_endpoint(
    club_id: int,
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return update_activity(
        db=db,
        club_id=club_id,
        activity_id=activity_id,
        activity_in=activity_in,
        current_user=current_user,
    )


@router.delete(
    "/{club_id}/activities/{activity_id}",
    status_code=status.HTTP_200_OK,
)
def delete_club_activity_endpoint(
    club_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return delete_activity(
        db=db, club_id=club_id, activity_id=activity_id, current_user=current_user
    )
