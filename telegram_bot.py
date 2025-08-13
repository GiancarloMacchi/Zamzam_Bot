# telegram_bot.py
import os
from telegram import Bot
from telegram.error import TelegramError

try:
    from PIL import Image
except ImportError:
    Image = None  # Pillow non disponibile

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(message, image_path=None):
    try:
        if image_path and os.path.exists(image_path):
            if Image:
                try:
                    with Image.open(image_path) as img:
                        img.verify()  # Verifica immagine valida
                except Exception as e:
                    print(f"[AVVISO] Immagine non valida ({e}), invio solo testo.")
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                    return
            with open(image_path, "rb") as img_file:
                bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img_file, caption=message)
        else:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as e:
        print(f"[ERRORE TELEGRAM] {e}")
    except Exception as e:
        print(f"[ERRORE GENERICO] {e}")
