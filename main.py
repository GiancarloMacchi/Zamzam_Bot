import os
import sys
from amazon_api import get_amazon_products
from telegram_bot import send_telegram_message

# Lista delle variabili d'ambiente richieste (senza RUN_ONCE)
REQUIRED_ENV_VARS = [
    "AMAZON_ACCESS_KEY",
    "AMAZON_SECRET_KEY",
    "AMAZON_ASSOCIATE_TAG",
    "AMAZON_COUNTRY",
    "BITLY_TOKEN",
    "ITEM_COUNT",
    "KEYWORDS",
    "MIN_SAVE",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID"
]

def check_env_vars():
    """Controlla che tutte le variabili d'ambiente richieste siano presenti."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        print(f"❌ Mancano le seguenti variabili d'ambiente: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("✅ Tutte le variabili d'ambiente sono presenti.")

def main():
    check_env_vars()

    keywords = os.getenv("KEYWORDS")
    item_count = int(os.getenv("ITEM_COUNT", "10"))
    min_save = float(os.getenv("MIN_SAVE", "0"))

    products = get_amazon_products(
        keywords=keywords,
        amazon_access_key=os.getenv("AMAZON_ACCESS_KEY"),
        amazon_secret_key=os.getenv("AMAZON_SECRET_KEY"),
        amazon_tag=os.getenv("AMAZON_ASSOCIATE_TAG")
    )

    if not products:
        print("⚠ Nessun prodotto trovato.")
        return

    for product in products[:item_count]:
        title = product.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
        price_info = product.get("Offers", {}).get("Listings", [{}])[0].get("Price", {})
        price = price_info.get("DisplayAmount", "Prezzo non disponibile")

        message = f"🛒 {title}\n💰 {price}"
        send_telegram_message(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"), message)

if __name__ == "__main__":
    main()
