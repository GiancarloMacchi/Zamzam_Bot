from telegram import Bot
from telegram.error import TelegramError
from PIL import Image
import io
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_telegram_message(token, chat_id, text, image_url=None):
    bot = Bot(token=token)
    try:
        if image_url:
            # Scarica l'immagine
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Carica con Pillow per validazione
            image = Image.open(io.BytesIO(response.content))
            image.verify()  # Verifica integrità dell'immagine

            # Reinvia in formato corretto
            image = Image.open(io.BytesIO(response.content))
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_byte_arr.seek(0)

            bot.send_photo(chat_id=chat_id, photo=img_byte_arr, caption=text)
        else:
            bot.send_message(chat_id=chat_id, text=text)

        logger.info("Messaggio inviato con successo a Telegram.")

    except (TelegramError, requests.RequestException, IOError) as e:
        logger.error(f"Errore nell'invio del messaggio Telegram: {e}")
