# app/router.py

from files.file_router import route_file
from app.telegram_handler import extract_telegram_message


def route_update(update: dict) -> dict:
    """
    Router utama buat nentuin update Telegram ini:
    - text
    - document
    - photo
    - unsupported
    """

    message = update.get("message")
    if not message:
        return {"type": "unsupported", "reason": "No message found"}

    # TEXT
    if "text" in message and message["text"]:
        chat = message.get("chat", {})
        return {
            "type": "text",
            "chat_id": chat.get("id"),
            "text": message["text"].strip(),
        }

    # DOCUMENT
    if "document" in message:
        chat = message.get("chat", {})
        document = message["document"]

        return {
            "type": "document",
            "chat_id": chat.get("id"),
            "file_id": document.get("file_id"),
            "file_name": document.get("file_name"),
            "mime_type": document.get("mime_type"),
        }

    # PHOTO
    if "photo" in message:
        chat = message.get("chat", {})
        photos = message["photo"]

        # Telegram photo array: ambil resolusi paling gede
        biggest = photos[-1] if photos else {}

        return {
            "type": "photo",
            "chat_id": chat.get("id"),
            "file_id": biggest.get("file_id"),
            "file_name": "telegram_photo.jpg",
            "mime_type": "image/jpeg",
            "caption": message.get("caption", "").strip(),
        }

    return {"type": "unsupported", "reason": "Unsupported message type"}