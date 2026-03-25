# app/telegram_handler.py

import os
from pathlib import Path

import requests

from app.response_sender import send_ai_response, send_error_message
from memory.chat_store import save_message, get_recent_messages
from llm.prompt_builder import build_chat_prompt
from llm.llm_client import (
    generate_response,
    generate_file_response,
    generate_image_response,
)
from files.file_router import route_file
from prompts.file_analyst_prompt import build_file_analysis_prompt


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
TELEGRAM_FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}"

TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)


def extract_telegram_message(update: dict) -> tuple[int | None, str | None]:
    """
    Ambil chat_id dan text dari payload Telegram.
    Balikin (chat_id, user_text).
    Kalau format tidak sesuai, balikin (None, None).
    """
    message = update.get("message")
    if not message:
        return None, None

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    user_text = message.get("text")

    if not chat_id or not user_text:
        return None, None

    return chat_id, user_text.strip()


def _get_message(update: dict) -> dict | None:
    return update.get("message")


def _get_chat_id(message: dict) -> int | None:
    return message.get("chat", {}).get("id")


def _get_file_info(file_id: str) -> dict:
    """
    Ambil metadata file dari Telegram getFile.
    """
    response = requests.get(
        f"{TELEGRAM_API_URL}/getFile",
        params={"file_id": file_id},
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise ValueError("Gagal ambil info file dari Telegram.")

    return data["result"]


def _download_telegram_file(file_id: str, filename: str | None = None) -> str:
    """
    Download file Telegram ke local temp_uploads/.
    """
    file_info = _get_file_info(file_id)
    telegram_file_path = file_info.get("file_path")

    if not telegram_file_path:
        raise ValueError("Telegram gak ngasih file_path.")

    if not filename:
        filename = Path(telegram_file_path).name

    safe_name = Path(filename).name
    local_path = TEMP_DIR / safe_name

    response = requests.get(f"{TELEGRAM_FILE_URL}/{telegram_file_path}", timeout=60)
    response.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(response.content)

    return str(local_path)


def _handle_text_message(chat_id: int, user_text: str) -> None:
    """
    Flow chat text biasa.
    """
    save_message(chat_id=chat_id, role="user", content=user_text)

    recent_messages = get_recent_messages(chat_id=chat_id, limit=10)
    final_prompt = build_chat_prompt(recent_messages=recent_messages)

    ai_response = generate_response(prompt=final_prompt)

    save_message(chat_id=chat_id, role="assistant", content=ai_response)
    send_ai_response(chat_id=chat_id, ai_text=ai_response)


def _handle_document_message(chat_id: int, message: dict) -> None:
    """
    Flow file dokumen:
    Telegram doc -> download -> parse -> build prompt -> LLM -> reply
    """
    document = message.get("document", {})
    file_id = document.get("file_id")
    file_name = document.get("file_name", "uploaded_document")
    mime_type = document.get("mime_type")
    caption = (message.get("caption") or "").strip()

    if not file_id:
        send_error_message(chat_id=chat_id, error_text="File dokumen gak punya file_id bro.")
        return

    local_file_path = _download_telegram_file(file_id=file_id, filename=file_name)

    parsed = route_file(file_path=local_file_path, mime_type=mime_type)

    if parsed.get("status") != "success":
        send_error_message(chat_id=chat_id, error_text=parsed.get("text", "Dokumen gagal diproses."))
        return

    file_prompt = build_file_analysis_prompt(
        extracted_text=parsed.get("text", ""),
        user_question=caption,
        file_type=parsed.get("type", "document"),
        file_name=parsed.get("meta", {}).get("filename", file_name),
    )

    ai_response = generate_file_response(prompt=file_prompt)

    save_message(
        chat_id=chat_id,
        role="user",
        content=f"[Uploaded document: {file_name}] {caption}".strip()
    )
    save_message(
        chat_id=chat_id,
        role="assistant",
        content=ai_response
    )

    send_ai_response(chat_id=chat_id, ai_text=ai_response)


def _handle_photo_message(chat_id: int, message: dict) -> None:
    """
    Flow photo:
    Telegram photo -> download -> parse metadata -> prompt -> multimodal LLM -> reply
    """
    photos = message.get("photo", [])
    caption = (message.get("caption") or "").strip()

    if not photos:
        send_error_message(chat_id=chat_id, error_text="Foto gak ketemu bro.")
        return

    biggest_photo = photos[-1]
    file_id = biggest_photo.get("file_id")

    if not file_id:
        send_error_message(chat_id=chat_id, error_text="Foto gak punya file_id bro.")
        return

    local_file_path = _download_telegram_file(
        file_id=file_id,
        filename="telegram_photo.jpg"
    )

    parsed = route_file(file_path=local_file_path, mime_type="image/jpeg")

    if parsed.get("status") != "success":
        send_error_message(chat_id=chat_id, error_text=parsed.get("text", "Gambar gagal diproses."))
        return

    file_prompt = build_file_analysis_prompt(
        extracted_text=parsed.get("text", ""),
        user_question=caption or "Analisis gambar ini dan jelaskan isi utamanya.",
        file_type=parsed.get("type", "image"),
        file_name=parsed.get("meta", {}).get("filename", "telegram_photo.jpg"),
    )

    ai_response = generate_image_response(
        prompt=file_prompt,
        image_path=local_file_path,
    )

    save_message(
        chat_id=chat_id,
        role="user",
        content=f"[Uploaded image] {caption}".strip()
    )
    save_message(
        chat_id=chat_id,
        role="assistant",
        content=ai_response
    )

    send_ai_response(chat_id=chat_id, ai_text=ai_response)


def handle_telegram_update(update: dict) -> None:
    """
    Flow utama:
    - Text biasa
    - Dokumen
    - Foto
    """
    message = _get_message(update)
    if not message:
        return

    chat_id = _get_chat_id(message)
    if not chat_id:
        return

    try:
        if message.get("text"):
            user_text = message["text"].strip()
            _handle_text_message(chat_id=chat_id, user_text=user_text)
            return

        if message.get("document"):
            _handle_document_message(chat_id=chat_id, message=message)
            return

        if message.get("photo"):
            _handle_photo_message(chat_id=chat_id, message=message)
            return

        send_error_message(chat_id=chat_id, error_text="Tipe pesan ini belum didukung bro.")

    except Exception as error:
        print(f"[TELEGRAM_HANDLER_ERROR] {error}")
        send_error_message(chat_id=chat_id, error_text="Ada error pas proses request lu bro.")