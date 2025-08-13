import os
from dotenv import load_dotenv
from amazon_client import get_items

load_dotenv()

print("🚀 Avvio Amazon Bot in modalità DEBUG...")
print(f"🌍 Paese Amazon: {os.getenv('AMAZON_COUNTRY')}")
print(f"🔍 Parole chiave: {os.getenv('KEYWORDS')}")
print(f"📦 Numero massimo risultati: {os.getenv('ITEM_COUNT')}")

get_items()

print("✅ Esecuzione completata. Controlla il file amazon_debug.json.")
