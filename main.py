import os
from dotenv import load_dotenv
from telegram import Bot
from amazon_api import cerca_prodotti
from bitlyshortener import Shortener

load_dotenv()

# ✅ Secrets da GitHub
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
KEYWORDS = os.getenv("KEYWORDS", "offerte")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

# ✅ Setup bot e Bitly
bot = Bot(token=TELEGRAM_BOT_TOKEN)
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=8192)

def formatta_prodotto(p):
    short_url = shortener.shorten_urls([p["link"]])[0]
    return f"📦 {p['titolo']}\n💰 Prezzo: {p['prezzo']}\n🔗 {short_url}"

def invia_offerte():
    prodotti = cerca_prodotti(KEYWORDS, ITEM_COUNT)
    if not prodotti:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Nessuna offerta trovata.")
        return
    for p in prodotti:
        try:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=formatta_prodotto(p))
        except Exception as e:
            print(f"Errore invio prodotto: {e}")

if __name__ == "__main__":
    invia_offerte()
    if not RUN_ONCE:
        print("Modalità continua disabilitata in questa versione.")
