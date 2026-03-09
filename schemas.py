from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ── Auth ──────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Users ─────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Folders ───────────────────────────────────────
class FolderCreate(BaseModel):
    name: str
    path: str  # реальный путь на диске


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None


class FolderOut(BaseModel):
    id: int
    name: str
    path: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Access ────────────────────────────────────────
class AccessGrant(BaseModel):
    user_id: int
    folder_id: int


# ── Gallery ───────────────────────────────────────
class PhotoItem(BaseModel):
    name: str
    path: str


class FolderItem(BaseModel):
    name: str
    folder_id: int
    sub_path: str
    count: int


class DirectoryListing(BaseModel):
    folders: list[FolderItem]
    photos: list[PhotoItem]
