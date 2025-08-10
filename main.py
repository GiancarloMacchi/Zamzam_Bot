import os
import time
import schedule
from amazon_api import get_amazon_products
from telegram_bot import send_telegram_message

# Funzione per prendere la prima variabile d'ambiente trovata tra più nomi
def getenv_first(*names, default=None):
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    return default

# Legge le variabili d'ambiente (con valori di default se non presenti)
AMAZON_ACCESS_KEY = getenv_first("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = getenv_first("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = getenv_first("AMAZON_ASSOCIATE_TAG")
AMAZON_REGION = getenv_first("AMAZON_REGION", "IT")
TELEGRAM_BOT_TOKEN = getenv_first("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = getenv_first("TELEGRAM_CHAT_ID")

# FIX per evitare errore se RUN_ONCE è None
RUN_ONCE = (getenv_first("RUN_ONCE", "true") or "true").lower() in ("1", "true", "yes")

# Funzione principale del bot
def run_bot():
    print("🚀 Avvio bot Amazon...")
    products = get_amazon_products(
        amazon_access_key=AMAZON_ACCESS_KEY,
        amazon_secret_key=AMAZON_SECRET_KEY,
        amazon_tag=AMAZON_ASSOCIATE_TAG,
        amazon_region=AMAZON_REGION
    )

    if not products:
        print("❌ Nessun prodotto trovato.")
        return

    for product in products:
        message = f"📦 {product['title']}\n💰 Prezzo: {product['price']}\n🔗 {product['url']}"
        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
        time.sleep(1)  # Pausa per evitare spam

# Se RUN_ONCE è True → esegue solo una volta (utile per GitHub Actions)
if RUN_ONCE:
    run_bot()
else:
    # Esegue ogni ora (utile per esecuzione continua)
    schedule.every(1).hours.do(run_bot)
    print("⏳ Bot in attesa, esecuzione ogni ora...")
    while True:
        schedule.run_pending()
        time.sleep(60)
