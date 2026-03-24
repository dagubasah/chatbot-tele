# llm/prompt_builder.py

from typing import List, Dict


SYSTEM_PROMPT = """
Kamu adalah asisten AI Telegram yang membantu user dengan jelas, ringkas, cerdas, dan relevan.
Gunakan konteks percakapan terakhir jika memang membantu menjawab.
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


def build_chat_prompt(recent_messages: List[Dict]) -> str:
    """
    Susun prompt final untuk LLM dari system prompt + recent context.
    """
    conversation_context = format_recent_messages(recent_messages)

    final_prompt = f"""
{SYSTEM_PROMPT}

Berikut adalah riwayat percakapan terbaru:
{conversation_context}

Balaslah pesan user terbaru dengan memperhatikan konteks di atas bila relevan.
""".strip()

    return final_prompt