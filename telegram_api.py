import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text, image_url=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}"

    if image_url:
        data = {
            "chat_id": CHAT_ID,
            "caption": text,
            "parse_mode": "HTML"
        }
        files = {
            "photo": requests.get(image_url, stream=True).raw
        }
        requests.post(f"{base_url}/sendPhoto", data=data, files=files)
    else:
        data = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        requests.post(f"{base_url}/sendMessage", data=data)
