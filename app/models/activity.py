from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy import ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


# Bảng hoạt động câu lạc bộ
class Club_activitiesModel(Base):
    __tablename__ = "Club_activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("Clubs.club_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    assignee_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    created_by = Column(Integer, ForeignKey("Users.user_id"), nullable=False)

    status = Column(Enum("TODO", "IN_PROGRESS", "DONE"), default="TODO", nullable=False)
    priority = Column(Enum("LOW", "MEDIUM", "HIGH"), default="MEDIUM", nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.now, nullable=False)

    # Relationship
    club = relationship("ClubModel", back_populates="activities")
    assignee = relationship(
        "UserModel", foreign_keys=[assignee_id], back_populates="assigned_activities"
    )
    creator = relationship(
        "UserModel", foreign_keys=[created_by], back_populates="created_activities"
    )
    comments = relationship("CommentsModel", back_populates="activity")
    attachments = relationship("AttachmentsModel", back_populates="activity")
