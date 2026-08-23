from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy import Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


# Bảng lịch sử bình luận
class CommentsModel(Base):
    __tablename__ = "Comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(
        Integer, ForeignKey("Club_activities.activity_id"), nullable=True
    )
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    # Relationship
    activity = relationship("Club_activitiesModel", back_populates="comments")
    user = relationship("UserModel", back_populates="comments")


# Bảng file đính kèm
class AttachmentsModel(Base):
    __tablename__ = "Attachments"

    attachment_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(
        Integer, ForeignKey("Club_activities.activity_id"), nullable=True
    )
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    file_path = Column(String(255), nullable=False, unique=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    # Relationship
    activity = relationship("Club_activitiesModel", back_populates="attachments")
    user = relationship("UserModel", back_populates="attachments")


# Bảng lịch sử thao tác
class Activity_logsModel(Base):
    __tablename__ = "activity_logs"

    activity_logs_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(Enum("CLUB", "MEMBER", "ACTIVITY"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    # Relationship
    user = relationship("UserModel", back_populates="activity_logs")


# Bảng refresh_tokens
class Refresh_tokensModel(Base):
    __tablename__ = "refresh_tokens"

    ref_token_id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, default=datetime.now(), nullable=False)
    created_at = Column(DateTime)
    user_agent = Column(String(255), nullable=True)

    # Relationship
    user = relationship("UserModel", back_populates="refresh_tokens")
