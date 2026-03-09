from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Folder, UserFolderAccess, User
from services.gallery_service import list_directory, resolve_photo_path
from services.thumbnail_service import get_thumbnail
from dependencies import get_current_user

router = APIRouter(tags=["gallery"])

IMAGE_MIME = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.png': 'image/png', '.gif': 'image/gif',
    '.webp': 'image/webp', '.bmp': 'image/bmp',
    '.tiff': 'image/tiff', '.heic': 'image/heic',
}


def _get_accessible_folder(folder_id: int, user: User, db: Session) -> Folder:
    """Повертає папку якщо юзер має до неї доступ."""
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Папку не знайдено")

    if not user.is_admin:
        access = db.query(UserFolderAccess).filter_by(user_id=user.id, folder_id=folder_id).first()
        if not access:
            raise HTTPException(status_code=403, detail="Немає доступу до цієї папки")

    return folder


# ── Список доступних папок для юзера ──────────────
@router.get("/api/folders")
def get_folders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.is_admin:
        folders = db.query(Folder).all()
    else:
        folders = [a.folder for a in user.folder_access]

    return [{"id": f.id, "name": f.name} for f in folders]


# ── Вміст папки (з навігацією по підпапках) ───────
@router.get("/api/list")
def list_folder(
    folder_id: int = Query(...),
    sub_path: str = Query(default=""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    folder = _get_accessible_folder(folder_id, user, db)
    return list_directory(folder.path, sub_path, folder_id)


# ── Оригінальне фото ───────────────────────────────
@router.get("/photo")
def get_photo(
    path: str = Query(...),  # формат: "folder_id/відносний/шлях.jpg"
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    folder_id, rel_path = _parse_path(path)
    folder = _get_accessible_folder(folder_id, user, db)

    file_path = resolve_photo_path(folder.path, rel_path)
    if not file_path:
        raise HTTPException(status_code=404, detail="Фото не знайдено")

    mime = IMAGE_MIME.get(file_path.suffix.lower(), "application/octet-stream")
    return FileResponse(file_path, media_type=mime, headers={"Cache-Control": "public, max-age=86400"})


# ── Мініатюра ──────────────────────────────────────
@router.get("/thumb")
def get_thumb(
    path: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    folder_id, rel_path = _parse_path(path)
    folder = _get_accessible_folder(folder_id, user, db)

    file_path = resolve_photo_path(folder.path, rel_path)
    if not file_path:
        raise HTTPException(status_code=404, detail="Фото не знайдено")

    thumb_path = get_thumbnail(file_path)
    return FileResponse(thumb_path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})


def _parse_path(path: str) -> tuple[int, str]:
    """Розбирає "folder_id/rel/path" → (folder_id, "rel/path")"""
    parts = path.split("/", 1)
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Невірний формат шляху")
    try:
        folder_id = int(parts[0])
    except ValueError:
        raise HTTPException(status_code=400, detail="Невірний folder_id")
    return folder_id, parts[1]
