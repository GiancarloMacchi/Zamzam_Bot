import json
import os
from amazon_client import get_items
from telegram_bot import send_telegram_message

print("🚀 Avvio Amazon Bot...")
print(f"🌍 Paese Amazon: {os.getenv('AMAZON_COUNTRY')}")
print(f"🔍 Parole chiave: {os.getenv('KEYWORDS')}")
print(f"📉 Sconto minimo: {os.getenv('MIN_SAVE')}%")
print(f"📦 Numero massimo risultati: {os.getenv('ITEM_COUNT')}")

try:
    items = get_items()

    # Salva dati grezzi per debug
    debug_data = []
    for item in items:
        debug_data.append(item.__dict__ if hasattr(item, '__dict__') else str(item))

    with open("amazon_debug.json", "w", encoding="utf-8") as f:
        json.dump(debug_data, f, ensure_ascii=False, indent=4)

    print("💾 File amazon_debug.json salvato per il debug.")

    # Se vuoi mandare solo offerte filtrate, metti qui la logica
    for item in items:
        send_telegram_message(f"{item.title} - {item.detail_page_url}")

except Exception as e:
    print("❌ Errore durante il recupero degli articoli da Amazon API:")
    print(e)
