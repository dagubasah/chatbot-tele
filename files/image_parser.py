# files/image_parser.py

from pathlib import Path
from PIL import Image


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def guess_image_category(width: int, height: int) -> str:
    ratio = width / height if height else 1

    if ratio > 1.7:
        return "wide_image_or_screenshot"
    if ratio < 0.8:
        return "portrait_image"
    return "standard_image"


def parse_image(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {
            "type": "image",
            "status": "error",
            "text": "File gambar tidak ditemukan.",
            "meta": {"file_path": file_path},
        }

    extension = path.suffix.lower()

    if extension not in SUPPORTED_IMAGE_EXTENSIONS:
        return {
            "type": "image",
            "status": "error",
            "text": f"Format gambar {extension} belum didukung.",
            "meta": {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
            },
        }

    try:
        # validasi file image dulu
        with Image.open(path) as img:
            img.verify()

        # buka ulang setelah verify untuk ambil metadata
        with Image.open(path) as img:
            width, height = img.size
            image_format = img.format
            image_mode = img.mode

        file_size_bytes = path.stat().st_size
        category = guess_image_category(width, height)

        description_text = (
            f"Gambar berhasil dimuat. "
            f"Format: {image_format}. "
            f"Ukuran: {width}x{height} piksel. "
            f"Mode warna: {image_mode}. "
            f"Kategori kasar: {category}. "
            f"Siap dianalisis lebih lanjut oleh model vision."
        )

        return {
            "type": "image",
            "status": "success",
            "text": description_text,
            "meta": {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
                "format": image_format,
                "width": width,
                "height": height,
                "mode": image_mode,
                "category": category,
                "file_size_bytes": file_size_bytes,
            },
        }

    except Exception as e:
        return {
            "type": "image",
            "status": "error",
            "text": f"Gagal membaca gambar: {str(e)}",
            "meta": {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
            },
        }