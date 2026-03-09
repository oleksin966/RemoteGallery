from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Folder, UserFolderAccess
from schemas import UserCreate, UserUpdate, UserOut, FolderCreate, FolderUpdate, FolderOut, AccessGrant
from services.auth_service import hash_password
from dependencies import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])


# ══════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Користувач з таким логіном вже існує")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        is_admin=data.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if data.username is not None:
        existing = db.query(User).filter(User.username == data.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Логін вже зайнятий")
        user.username = data.username

    if data.password is not None:
        user.password_hash = hash_password(data.password)

    if data.is_admin is not None:
        user.is_admin = data.is_admin

    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Не можна видалити самого себе")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    db.delete(user)
    db.commit()


# ══════════════════════════════════════════
#  FOLDERS
# ══════════════════════════════════════════

@router.get("/folders", response_model=list[FolderOut])
def list_folders(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return db.query(Folder).all()


@router.post("/folders", response_model=FolderOut, status_code=201)
def create_folder(data: FolderCreate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    folder = Folder(name=data.name, path=data.path)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.put("/folders/{folder_id}", response_model=FolderOut)
def update_folder(folder_id: int, data: FolderUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Папку не знайдено")

    if data.name is not None:
        folder.name = data.name
    if data.path is not None:
        folder.path = data.path

    db.commit()
    db.refresh(folder)
    return folder


@router.delete("/folders/{folder_id}", status_code=204)
def delete_folder(folder_id: int, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Папку не знайдено")

    db.delete(folder)
    db.commit()


# ══════════════════════════════════════════
#  ACCESS
# ══════════════════════════════════════════

@router.get("/access/{user_id}", response_model=list[FolderOut])
def get_user_access(user_id: int, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return [a.folder for a in user.folder_access]


@router.post("/access", status_code=201)
def grant_access(data: AccessGrant, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    exists = db.query(UserFolderAccess).filter_by(user_id=data.user_id, folder_id=data.folder_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Доступ вже надано")

    db.add(UserFolderAccess(user_id=data.user_id, folder_id=data.folder_id))
    db.commit()
    return {"ok": True}


@router.delete("/access")
def revoke_access(data: AccessGrant, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    access = db.query(UserFolderAccess).filter_by(user_id=data.user_id, folder_id=data.folder_id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Доступ не знайдено")

    db.delete(access)
    db.commit()
    return {"ok": True}
