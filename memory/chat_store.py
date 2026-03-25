# memory/chat_store.py

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any


CHAT_HISTORY_PATH = "logs/chat_history.json"
MAX_HISTORY_PER_CHAT = 100


def ensure_chat_history_file() -> None:
    """
    Pastikan file logs/chat_history.json ada.
    Kalau belum ada, bikin file kosong berupa list JSON.
    """
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=2)


def load_chat_history() -> List[Dict[str, Any]]:
    """
    Load seluruh riwayat chat dari file JSON.
    """
    ensure_chat_history_file()

    try:
        with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_chat_history(messages: List[Dict[str, Any]]) -> None:
    """
    Simpan seluruh riwayat chat ke file JSON.
    """
    ensure_chat_history_file()

    with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)


def save_message(chat_id: int, role: str, content: str, message_type: str = "text") -> None:
    """
    Simpan 1 pesan ke chat history.

    role: user / assistant / system
    message_type: text / document / image / summary / system
    """
    if not content or not content.strip():
        return

    messages = load_chat_history()

    new_message = {
        "chat_id": chat_id,
        "role": role,
        "content": content.strip(),
        "message_type": message_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    messages.append(new_message)

    # Batasin history per chat biar file gak gendut brutal
    per_chat_messages = [m for m in messages if m.get("chat_id") == chat_id]
    if len(per_chat_messages) > MAX_HISTORY_PER_CHAT:
        excess_count = len(per_chat_messages) - MAX_HISTORY_PER_CHAT
        trimmed = []
        removed = 0

        for msg in messages:
            if msg.get("chat_id") == chat_id and removed < excess_count:
                removed += 1
                continue
            trimmed.append(msg)

        messages = trimmed

    save_chat_history(messages)


def get_recent_messages(chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Ambil recent messages berdasarkan chat_id.
    Default ambil 10 terakhir.
    """
    messages = load_chat_history()

    filtered_messages = [
        message for message in messages
        if message.get("chat_id") == chat_id
    ]

    return filtered_messages[-limit:]


def clear_chat_history(chat_id: int | None = None) -> None:
    """
    Hapus history.
    Kalau chat_id diisi -> hapus history untuk chat itu aja.
    Kalau None -> hapus semua.
    """
    if chat_id is None:
        save_chat_history([])
        return

    messages = load_chat_history()

    filtered_messages = [
        message for message in messages
        if message.get("chat_id") != chat_id
    ]

    save_chat_history(filtered_messages)