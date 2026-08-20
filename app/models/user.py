from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


# Bảng người dùng
class UserModel(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum("USER", "ADMIN"), default="USER", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    owned_clubs = relationship("ClubModel", back_populates="owner")
    club_memberships = relationship("Club_membersModel", back_populates="user")
    assigned_activities = relationship(
        "Club_activitiesModel", back_populates="assignee"
    )

    # Nâng cao
    comments = relationship("CommentsModel", back_populates="user")
    attachments = relationship("AttachmentsModel", back_populates="user")
    activity_logs = relationship("Activity_logsModel", back_populates="user")
    refresh_tokens = relationship("Refresh_tokensModel", back_populates="user")
