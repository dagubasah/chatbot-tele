# app/telegram_handler.py

from app.response_sender import send_ai_response, send_error_message
from memory.chat_store import save_message, get_recent_messages
from llm.prompt_builder import build_chat_prompt
from llm.llm_client import generate_response


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


def handle_telegram_update(update: dict) -> None:
    """
    Flow utama:
    1. Extract pesan user
    2. Simpan pesan user
    3. Ambil recent 10 context
    4. Build prompt
    5. Generate response dari LLM
    6. Simpan jawaban AI
    7. Kirim ke Telegram
    """
    chat_id, user_text = extract_telegram_message(update)

    if not chat_id or not user_text:
        return

    try:
        # Simpan pesan user dulu
        save_message(chat_id=chat_id, role="user", content=user_text)

        # Ambil recent 10 messages
        recent_messages = get_recent_messages(chat_id=chat_id, limit=10)

        # Build prompt dari recent context
        final_prompt = build_chat_prompt(recent_messages=recent_messages)

        # Minta jawaban ke LLM
        ai_response = generate_response( prompt=final_prompt)

        # Simpan jawaban AI
        save_message(chat_id=chat_id, role="assistant", content=ai_response)

        # Kirim balik ke Telegram
        send_ai_response(chat_id=chat_id, ai_text=ai_response)

    except Exception as error:
        print(f"[TELEGRAM_HANDLER_ERROR] {error}")
        send_error_message(chat_id=chat_id, error_text="Ada error pas proses chat lu bro.")

        #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA