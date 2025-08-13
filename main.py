from amazon_client import get_items
from telegram_bot import send_telegram_message
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    send_telegram_message("🔍 Recupero articoli da Amazon...")

    items = get_items()
    if not items:
        send_telegram_message("❌ Nessuna offerta trovata o errore nelle API Amazon.")
        return

    for item in items:
        message = (
            f"📦 <b>{item['title']}</b>\n"
            f"💰 Prezzo: {item['price']} {item['currency']}\n"
            f"💸 Sconto: {item['saving']}%\n"
            f"🔗 <a href='{item['url']}'>Acquista ora</a>"
        )
        send_telegram_message(message)

if __name__ == "__main__":
    main()
