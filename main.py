import os
from dotenv import load_dotenv
from telegram import Bot
from amazon_api import cerca_prodotti

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "offerte")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

bot = Bot(token=TELEGRAM_BOT_TOKEN)


def invia_offerte():
    prodotti = cerca_prodotti(KEYWORDS, ITEM_COUNT, MIN_SAVE)
    if not prodotti:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Nessun prodotto trovato.")
        return

    for p in prodotti:
        messaggio = (
            f"📦 {p['titolo']}\n"
            f"💰 Prezzo: {p['prezzo']}€\n"
            f"🏷 Sconto: {p['sconto']}%\n"
            f"🔗 {p['link']}"
        )
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio)


if __name__ == "__main__":
    invia_offerte()
