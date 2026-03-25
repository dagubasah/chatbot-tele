# llm/prompt_builder.py

from typing import List, Dict


SYSTEM_PROMPT = """
Kamu adalah asisten AI Telegram yang membantu user dengan jelas, ringkas, cerdas, dan relevan.
Gunakan konteks percakapan terakhir hanya jika memang membantu menjawab.
Kalau konteks sebelumnya tidak relevan, fokus ke pertanyaan terbaru user.
Jangan mengarang detail yang tidak ada.
Jawab dengan bahasa yang natural dan mudah dipahami.
""".strip()


def format_recent_messages(recent_messages: List[Dict]) -> str:
    """
    Ubah recent messages dari chat_store jadi teks dialog yang rapi.
    """
    if not recent_messages:
        return "Belum ada riwayat percakapan sebelumnya."

    lines = []

    for msg in recent_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "").strip()

        if not content:
            continue

        if role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Assistant: {content}")
        else:
            lines.append(f"{role.capitalize()}: {content}")

    return "\n".join(lines)


def get_latest_user_message(recent_messages: List[Dict]) -> str:
    """
    Ambil pesan user terakhir dari recent_messages.
    """
    for msg in reversed(recent_messages):
        if msg.get("role") == "user":
            content = msg.get("content", "").strip()
            if content:
                return content

    return ""


def build_chat_prompt(recent_messages: List[Dict]) -> str:
    """
    Susun prompt final untuk LLM dari system prompt + recent context + fokus ke pesan user terbaru.
    """
    conversation_context = format_recent_messages(recent_messages)
    latest_user_message = get_latest_user_message(recent_messages)

    if not latest_user_message:
        latest_user_message = "Tidak ada pesan user terbaru yang terbaca."

    final_prompt = f"""
{SYSTEM_PROMPT}

Riwayat percakapan terbaru:
{conversation_context}

Pesan user terbaru yang harus kamu jawab:
User: {latest_user_message}

Instruksi:
- Jawab pesan user terbaru di atas.
- Gunakan riwayat percakapan hanya jika relevan.
- Kalau pertanyaan terbaru tidak butuh konteks lama, fokus saja ke pertanyaan terbaru.
- Jangan mengarang informasi yang tidak disebutkan user.

Sekarang berikan jawaban terbaikmu.
""".strip()

    return final_prompt