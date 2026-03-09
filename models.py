from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    folder_access = relationship("UserFolderAccess", back_populates="user", cascade="all, delete")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)  # реальный путь на диске
    created_at = Column(DateTime, default=datetime.utcnow)

    user_access = relationship("UserFolderAccess", back_populates="folder", cascade="all, delete")


class UserFolderAccess(Base):
    __tablename__ = "user_folder_access"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), primary_key=True)

    user = relationship("User", back_populates="folder_access")
    folder = relationship("Folder", back_populates="user_access")
