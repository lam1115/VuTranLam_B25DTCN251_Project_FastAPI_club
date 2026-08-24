from sqlalchemy.orm import Session
from app.models.advanced_models import Activity_logsModel


def create_activity_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,  # "CLUB" hoặc "MEMBER" hoặc "ACTIVITY"
    entity_id: int,
    details: str,
):
    log_entry = Activity_logsModel(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log_entry)
