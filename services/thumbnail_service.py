from pathlib import Path
from PIL import Image
import hashlib
from config import settings


THUMB_SIZE = (400, 400)


def get_thumbnail(photo_path: Path) -> Path:
    """
    Повертає шлях до мініатюри. Якщо немає — генерує і кешує.
    """
    # Унікальне ім'я кешу по хешу шляху
    key = hashlib.md5(str(photo_path).encode()).hexdigest()
    thumb_path = Path(settings.THUMBS_DIR) / f"{key}.jpg"

    if thumb_path.exists():
        return thumb_path

    try:
        with Image.open(photo_path) as img:
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)
            # Конвертуємо в RGB (для HEIC/PNG з прозорістю)
            if img.mode in ("RGBA", "P", "LA"):
                background = Image.new("RGB", img.size, (20, 20, 22))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            img.save(thumb_path, "JPEG", quality=80, optimize=True)
    except Exception:
        # Якщо не вдалось — повертаємо оригінал
        return photo_path

    return thumb_path
