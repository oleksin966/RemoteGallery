from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import socket

from database import engine, SessionLocal
from models import Base, User
from services.auth_service import hash_password
from config import settings
from routers import auth, admin, gallery


def create_default_admin():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        exists = db.query(User).filter(User.is_admin == True).first()
        if not exists:
            admin_user = User(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                is_admin=True,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print(f"  ✅ Адмін '{settings.ADMIN_USERNAME}' створено автоматично")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_default_admin()
    yield


app = FastAPI(title="📸 Remote Gallery", version="1.0.0", lifespan=lifespan)

# ── Підключаємо роутери ───────────────────────────
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(gallery.router)

# ── Статика (HTML файли) ──────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/admin-panel")
def admin_panel():
    return FileResponse("static/admin.html")


# ── Запуск ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            return "127.0.0.1"
        finally:
            s.close()

    ip = get_local_ip()
    print("=" * 50)
    print("  📸 Remote Gallery запущено!")
    print("=" * 50)
    print(f"  🌐 Локально:  http://localhost:8080")
    print(f"  📱 По Wi-Fi:  http://{ip}:8080")
    print(f"  🔧 Адмінка:   http://localhost:8080/admin-panel")
    print(f"  📖 API docs:  http://localhost:8080/docs")
    print("=" * 50)

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)