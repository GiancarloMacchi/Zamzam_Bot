import os
from dotenv import load_dotenv
from amazon_client import get_items
from telegram_bot import send_telegram_message

# Carica variabili ambiente
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def main():
    print("🔍 Recupero articoli da Amazon...")
    items = get_items()

    if not items:
        error_message = "❌ Nessuna offerta trovata o errore nelle API Amazon."
        print(error_message)
        send_telegram_message(BOT_TOKEN, CHAT_ID, error_message)
        return

    print(f"✅ {len(items)} offerte trovate. Invio a Telegram...")
    for item in items:
        try:
            message = (
                f"📦 {item['title']}\n"
                f"💰 {item['price']} {item['currency']}\n"
                f"💸 Sconto: {item['saving']}%\n"
                f"🔗 {item['url']}"
            )
            send_telegram_message(BOT_TOKEN, CHAT_ID, message)
        except Exception as e:
            print(f"Errore nell'invio di un messaggio Telegram: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Errore generale:")
        print(e)
