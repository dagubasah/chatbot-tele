# main.py

import time
import requests

from app.telegram_handler import handle_telegram_update
from config.telegram_config import TELEGRAM_API_URL


def get_updates(offset: int | None = None) -> dict:
    """
    Ambil update terbaru dari Telegram via long polling.
    """
    url = f"{TELEGRAM_API_URL}/getUpdates"

    params = {
        "timeout": 30,
    }

    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=35)
    response.raise_for_status()
    return response.json()


def run_bot() -> None:
    """
    Loop utama bot Telegram.
    """
    print("[BOT] nyala njing 😵🔥")

    offset = None

    while True:
        try:
            data = get_updates(offset=offset)

            if not data.get("ok"):
                print("[BOT] Telegram API balikin ok=False")
                time.sleep(1)
                continue

            updates = data.get("result", [])

            if updates:
                print(f"[BOT] dapet {len(updates)} update")

            for update in updates:
                try:
                    update_id = update.get("update_id")

                    if update_id is None:
                        print("[BOT] update tanpa update_id, skip")
                        continue

                    # biar gak double process
                    offset = update_id + 1

                    handle_telegram_update(update)

                except Exception as update_error:
                    print(f"[UPDATE_ERROR] {update_error}")

        except requests.RequestException as req_error:
            print(f"[MAIN_REQUEST_ERROR] {req_error}")
            time.sleep(3)

        except Exception as e:
            print(f"[MAIN_ERROR] {e}")
            time.sleep(3)


if __name__ == "__main__":
    run_bot()