# main.py

import time
import requests

from app.telegram_handler import handle_telegram_update
from config.telegram_config import TELEGRAM_API_URL


def get_updates(offset=None):
    url = f"{TELEGRAM_API_URL}/getUpdates"

    params = {
        "timeout": 30,
        "offset": offset
    }

    response = requests.get(url, params=params, timeout=35)
    response.raise_for_status()
    return response.json()


def run_bot():
    print("nyala njing😵😵😵😵😵😵😵")

    offset = None

    while True:
        try:
            data = get_updates(offset=offset)

            if not data.get("ok"):
                continue

            updates = data.get("result", [])

            for update in updates:
                update_id = update["update_id"]

                # biar gak double process
                offset = update_id + 1

                handle_telegram_update(update)

        except Exception as e:
            print(f"[MAIN_ERROR] {e}")
            time.sleep(3)


if __name__ == "__main__":
    run_bot()

#bismillah