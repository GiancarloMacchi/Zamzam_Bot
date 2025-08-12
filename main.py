import os
from dotenv import load_dotenv
from telegram import Bot
from amazon_api import cerca_prodotti

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "iphone")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def main():
    print(f"🔍 Avvio ricerca prodotti su Amazon...")
    print(f"   Keywords: {KEYWORDS}")
    print(f"   Numero massimo risultati: {ITEM_COUNT}")
    print(f"   Sconto minimo: {MIN_SAVE}%\n")

    prodotti = cerca_prodotti(KEYWORDS, ITEM_COUNT, MIN_SAVE)

    # 🔹 Log di debug: stampiamo i dati grezzi
    print("=== DEBUG: Prodotti restituiti da Amazon API ===")
    if not prodotti:
        print("(Nessun prodotto trovato)")
    else:
        for idx, p in enumerate(prodotti, start=1):
            print(f"{idx}. {p['titolo']}")
            print(f"   Prezzo offerta: {p['prezzo']}")
            print(f"   Prezzo listino: {p['prezzo_listino']}")
            print(f"   Sconto: {p['sconto']}%")
            print(f"   Link: {p['link']}\n")
    print("===============================================\n")

    # Invio su Telegram
    if prodotti:
        for p in prodotti:
            messaggio = (
                f"**{p['titolo']}**\n"
                f"💰 Prezzo: {p['prezzo']} €\n"
                f"💸 Prezzo di listino: {p['prezzo_listino']} €\n"
                f"📉 Sconto: {p['sconto']}%\n"
                f"🔗 [Acquista ora]({p['link']})"
            )
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, parse_mode="Markdown")
    else:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Nessun prodotto trovato.")

if __name__ == "__main__":
    main()
