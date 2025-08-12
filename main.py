import os
from telegram import Bot
from amazon_api import cerca_prodotti
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "iPhone")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def invia_messaggio(messaggio):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, parse_mode="HTML")
    except Exception as e:
        print(f"Errore invio messaggio Telegram: {e}")

def main():
    prodotti = cerca_prodotti(KEYWORDS, item_count=ITEM_COUNT, min_save=MIN_SAVE)

    if not prodotti:
        invia_messaggio("⚠ Nessun prodotto trovato.")
        return

    for p in prodotti:
        testo = (
            f"<b>{p['titolo']}</b>\n"
            f"💰 Prezzo: {p['prezzo']} €\n"
            f"🏷 Listino: {p['prezzo_listino']} €\n"
            f"📉 Sconto: {p['sconto']}%\n"
            f"🔗 <a href='{p['link']}'>Compra ora</a>"
        )
        invia_messaggio(testo)

if __name__ == "__main__":
    main()
