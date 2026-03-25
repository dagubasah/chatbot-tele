# files/file_router.py

from pathlib import Path

from files.document_parser import parse_document
from files.image_parser import parse_image


DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "text/plain",
}

IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

DOCUMENT_EXTENSIONS = {".pdf", ".txt"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def route_file(file_path: str, mime_type: str | None = None) -> dict:
    """
    Router file utama.
    Nentuin file ini masuk parser dokumen atau parser gambar.

    Output standar:
    {
        "type": "document" | "image" | "unsupported",
        "status": "success" | "error",
        "text": "...",
        "meta": {...}
    }
    """

    path = Path(file_path)

    if not path.exists():
        return {
            "type": "unsupported",
            "status": "error",
            "text": "File tidak ditemukan.",
            "meta": {
                "file_path": file_path,
                "mime_type": mime_type,
            },
        }

    extension = path.suffix.lower()

    if _is_image(mime_type, extension):
        return parse_image(file_path)

    if _is_document(mime_type, extension):
        return parse_document(file_path)

    return {
        "type": "unsupported",
        "status": "error",
        "text": f"Format file belum didukung: {mime_type or extension or 'unknown'}",
        "meta": {
            "file_path": file_path,
            "filename": path.name,
            "extension": extension,
            "mime_type": mime_type,
        },
    }


def _is_image(mime_type: str | None, extension: str) -> bool:
    if mime_type and mime_type.lower() in IMAGE_MIME_TYPES:
        return True
    return extension in IMAGE_EXTENSIONS


def _is_document(mime_type: str | None, extension: str) -> bool:
    if mime_type and mime_type.lower() in DOCUMENT_MIME_TYPES:
        return True
    return extension in DOCUMENT_EXTENSIONS