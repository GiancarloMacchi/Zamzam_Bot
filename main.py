import os
from dotenv import load_dotenv
from telegram import Bot
from amazon_client import get_items

# Carica variabili d'ambiente
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_message(text):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode="HTML", disable_notification=True)

if __name__ == "__main__":
    try:
        items = get_items()
        if items:
            for item in items:
                send_message(item)
        else:
            send_message("Nessun prodotto trovato oggi 🚫")
    except Exception as e:
        send_message(f"Errore nell'esecuzione del bot: {str(e)}")
