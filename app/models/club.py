from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy import ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


# Bảng câu lạc bộ
class ClubModel(Base):
    __tablename__ = "Clubs"

    club_id = Column(Integer, primary_key=True, index=True)
    club_name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    owner = relationship("UserModel", back_populates="owned_clubs")
    members = relationship("Club_membersModel", back_populates="club")
    activities = relationship("Club_activitiesModel", back_populates="club")


# Bảng thành viên câu lạc bộ
class Club_membersModel(Base):
    __tablename__ = "Club_members"

    club_id = Column(Integer, ForeignKey("Clubs.club_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    role = Column(Enum("OWNER", "MEMBER"), nullable=False)
    joined_at = Column(DateTime, default=datetime.now(), nullable=False)

    club = relationship("ClubModel", back_populates="members")
    user = relationship("UserModel", back_populates="club_memberships")
