# app/response_sender.py

import requests
from typing import Optional

from config.telegram_config import TELEGRAM_API_URL


MAX_TELEGRAM_MESSAGE_LENGTH = 4096


def split_message(text: str, max_length: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    """
    Memecah pesan panjang jadi beberapa bagian agar aman dikirim ke Telegram.
    Prioritas pecah di newline biar tetap enak dibaca.
    """
    if not text:
        return [""]

    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    for line in text.splitlines(keepends=True):
        if len(current_chunk) + len(line) <= max_length:
            current_chunk += line
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # kalau 1 line sendiri kepanjangan, paksa pecah
            while len(line) > max_length:
                chunks.append(line[:max_length].strip())
                line = line[max_length:]

            current_chunk = line

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def send_telegram_message(chat_id: int, text: str, parse_mode: Optional[str] = None) -> dict:
    """
    Mengirim 1 message ke Telegram.
    """
    url = f"{TELEGRAM_API_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def send_long_message(chat_id: int, text: str, parse_mode: Optional[str] = None) -> None:
    """
    Mengirim text panjang dalam beberapa chunk jika melebihi limit Telegram.
    """
    chunks = split_message(text)

    for chunk in chunks:
        send_telegram_message(chat_id=chat_id, text=chunk, parse_mode=parse_mode)


def send_error_message(chat_id: int, error_text: str = "Terjadi error saat memproses request.") -> None:
    """
    Helper untuk kirim pesan error yang konsisten.
    """
    safe_text = f"⚠️ {error_text}"
    send_telegram_message(chat_id=chat_id, text=safe_text)


def send_ai_response(chat_id: int, ai_text: str) -> None:
    """
    Fungsi utama untuk kirim response AI ke user.
    Bisa lu panggil langsung dari telegram_handler.py
    """
    if not ai_text or not ai_text.strip():
        ai_text = "Aing lagi blank kalem bro 😵 coba ulangi lagi."

    send_long_message(chat_id=chat_id, text=ai_text.strip())