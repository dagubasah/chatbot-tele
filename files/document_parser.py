# files/document_parser.py

import re
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


SUPPORTED_DOCUMENT_EXTENSIONS = {".txt", ".pdf"}


def _clean_text(text: str) -> str:
    """
    Bersihin whitespace berlebihan biar output lebih rapih.
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_document(file_path: str) -> dict:
    """
    Parse dokumen dan balikin output standar:
    {
        "type": "document",
        "status": "success" | "error",
        "text": "...",
        "meta": {...}
    }
    """
    path = Path(file_path)

    if not path.exists():
        return {
            "type": "document",
            "status": "error",
            "text": "File dokumen tidak ditemukan.",
            "meta": {"file_path": file_path},
        }

    extension = path.suffix.lower()

    if extension not in SUPPORTED_DOCUMENT_EXTENSIONS:
        return {
            "type": "document",
            "status": "error",
            "text": f"Format dokumen {extension} belum didukung.",
            "meta": {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
            },
        }

    try:
        if extension == ".txt":
            return _parse_txt(path)

        if extension == ".pdf":
            return _parse_pdf(path)

        return {
            "type": "document",
            "status": "error",
            "text": "Parser untuk format ini belum tersedia.",
            "meta": {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
            },
        }

    except Exception as e:
        return {
            "type": "document",
            "status": "error",
            "text": f"Gagal memproses dokumen: {str(e)}",
            "meta": {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
            },
        }


def _parse_txt(path: Path) -> dict:
    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    text = _clean_text(raw_text)

    if not text:
        return {
            "type": "document",
            "status": "error",
            "text": "File TXT kosong atau tidak mengandung teks yang bisa dibaca.",
            "meta": {
                "file_path": str(path),
                "filename": path.name,
                "extension": ".txt",
                "characters": 0,
            },
        }

    return {
        "type": "document",
        "status": "success",
        "text": text,
        "meta": {
            "file_path": str(path),
            "filename": path.name,
            "extension": ".txt",
            "characters": len(text),
        },
    }


def _parse_pdf(path: Path) -> dict:
    if PdfReader is None:
        return {
            "type": "document",
            "status": "error",
            "text": "Library pypdf belum terpasang. Install dulu dengan: pip install pypdf",
            "meta": {
                "file_path": str(path),
                "filename": path.name,
                "extension": ".pdf",
            },
        }

    reader = PdfReader(str(path))
    page_count = len(reader.pages)

    extracted_pages = []
    extracted_page_count = 0

    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_text = _clean_text(page_text)

        if page_text:
            extracted_pages.append(page_text)
            extracted_page_count += 1

    full_text = "\n\n".join(extracted_pages).strip()

    if not full_text:
        return {
            "type": "document",
            "status": "error",
            "text": "PDF berhasil dibuka, tapi teks tidak berhasil diekstrak. Kemungkinan PDF berupa scan/gambar.",
            "meta": {
                "file_path": str(path),
                "filename": path.name,
                "extension": ".pdf",
                "pages": page_count,
                "extracted_pages": 0,
                "characters": 0,
            },
        }

    return {
        "type": "document",
        "status": "success",
        "text": full_text,
        "meta": {
            "file_path": str(path),
            "filename": path.name,
            "extension": ".pdf",
            "pages": page_count,
            "extracted_pages": extracted_page_count,
            "characters": len(full_text),
        },
    }