import os
import time
from amazon_api import cerca_prodotti  # importa la tua funzione Amazon
from telegram import invia_messaggio   # importa la tua funzione Telegram

def check_env_vars():
    required_vars = [
        "AMAZON_ACCESS_KEY",
        "AMAZON_SECRET_KEY",
        "AMAZON_ASSOCIATE_TAG",
        "AMAZON_COUNTRY",
        "BITLY_TOKEN",
        "ITEM_COUNT",
        "KEYWORDS",
        "MIN_SAVE",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "RUN_ONCE"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Errore: variabili d'ambiente mancanti: {', '.join(missing_vars)}")
        return False
    return True

def main():
    print("🚀 Avvio bot Amazon...")

    # Controllo variabili
    if not check_env_vars():
        return

    keywords = os.getenv("KEYWORDS").split(",")
    min_save = int(os.getenv("MIN_SAVE"))
    item_count = int(os.getenv("ITEM_COUNT"))
    run_once = os.getenv("RUN_ONCE", "true").lower() == "true"

    while True:
        for keyword in keywords:
            prodotti = cerca_prodotti(keyword.strip(), min_save, item_count)
            for prodotto in prodotti:
                invia_messaggio(prodotto)

        if run_once:
            break

        time.sleep(3600)  # attesa 1 ora

if __name__ == "__main__":
    main()
