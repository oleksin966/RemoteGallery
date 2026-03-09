from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.heic'}


def list_directory(base_path: str, sub_path: str, folder_id: int) -> dict:
    """
    Читає вміст папки. Повертає підпапки і фото.
    base_path — реальний шлях на диску (з БД)
    sub_path  — відносний шлях всередині base_path (навігація юзера)
    folder_id — id папки в БД (для побудови URL)
    """
    base = Path(base_path)
    target = (base / sub_path).resolve()

    # Захист від виходу за межі дозволеної папки
    if not str(target).startswith(str(base.resolve())):
        return {"folders": [], "photos": []}

    folders, photos = [], []

    try:
        for item in sorted(target.iterdir()):
            if item.name.startswith('.'):
                continue

            if item.is_dir():
                count = sum(1 for f in item.rglob('*') if f.suffix.lower() in IMAGE_EXTENSIONS)
                rel = str(item.relative_to(base)).replace('\\', '/')
                folders.append({
                    "name": item.name,
                    "folder_id": folder_id,
                    "sub_path": rel,
                    "count": count,
                })

            elif item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                rel = str(item.relative_to(base)).replace('\\', '/')
                photos.append({
                    "name": item.name,
                    "path": f"{folder_id}/{rel}",  # folder_id/відносний шлях
                })

    except PermissionError:
        pass

    return {"folders": folders, "photos": photos}


def resolve_photo_path(base_path: str, rel_path: str) -> Path | None:
    """
    Повертає абсолютний шлях до фото або None якщо недоступно.
    rel_path — відносний шлях всередині base_path
    """
    base = Path(base_path)
    target = (base / rel_path).resolve()

    if not str(target).startswith(str(base.resolve())):
        return None
    if not target.is_file():
        return None
    return target
