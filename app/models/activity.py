from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy import ForeignKey, DateTime, Text
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
    status = Column(Enum("TODO", "IN_PROGRESS", "DONE"), nullable=False)
    priority = Column(Enum("LOW", "MEDIUM", "HIGH"), nullable=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    # Relationship
    club = relationship("ClubModel", back_populates="activities")
    assignee = relationship("UserModel", back_populates="assigned_activities")
    comments = relationship("CommentsModel", back_populates="activity")
    attachments = relationship("AttachmentsModel", back_populates="activity")
