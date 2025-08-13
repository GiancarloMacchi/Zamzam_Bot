import os
from dotenv import load_dotenv
from amazon_client import get_items
from telegram_bot import send_telegram_message

load_dotenv()

RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

print("🚀 Avvio Amazon Bot...")
print(f"🌍 Paese Amazon: {os.getenv('AMAZON_COUNTRY')}")
print(f"🔍 Parole chiave: {os.getenv('KEYWORDS')}")
print(f"📉 Sconto minimo: {os.getenv('MIN_SAVE')}%")
print(f"📦 Numero massimo risultati: {os.getenv('ITEM_COUNT')}")

try:
    items = get_items()
    if not items:
        print("⚠ Nessun articolo trovato con i criteri impostati.")
    else:
        for item in items:
            message = (
                f"📦 *{item['title']}*\n"
                f"💰 Prezzo: {item['price']} {item['currency']}\n"
                f"💸 Sconto: {item['saving']}%\n"
                f"🔗 [Vedi su Amazon]({item['url']})"
            )
            send_telegram_message(message)
except Exception as e:
    print("❌ Errore durante l'esecuzione del bot:")
    print(e)

if RUN_ONCE:
    print("✅ Esecuzione singola completata.")
