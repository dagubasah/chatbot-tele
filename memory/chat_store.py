# memory/chat_store.py

import json
import os
from datetime import datetime
from typing import List, Dict, Any


CHAT_HISTORY_PATH = "logs/chat_history.json"


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

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_chat_history(messages: List[Dict[str, Any]]) -> None:
    """
    Simpan seluruh riwayat chat ke file JSON.
    """
    with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)


def save_message(chat_id: int, role: str, content: str) -> None:
    """
    Simpan 1 pesan ke chat history.
    role: 'user' atau 'assistant'
    """
    if not content or not content.strip():
        return

    messages = load_chat_history()

    new_message = {
        "chat_id": chat_id,
        "role": role,
        "content": content.strip(),
        "timestamp": datetime.utcnow().isoformat()
    }

    messages.append(new_message)
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