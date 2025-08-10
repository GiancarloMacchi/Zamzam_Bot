import os
import sys
from amazon_api import get_amazon_products

# Lista delle variabili richieste (quelle che hai fissato e non vuoi cambiare)
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
    "TELEGRAM_CHAT_ID",
    "RUN_ONCE"
]

def check_env_vars():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        print(f"❌ Mancano le seguenti variabili d'ambiente: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("✅ Tutte le variabili d'ambiente sono presenti.")

def main():
    # 1. Controllo variabili
    check_env_vars()

    # 2. Lettura variabili
    amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
    amazon_secret_key = os.getenv("AMAZON_SECRET_KEY")
    amazon_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
    keywords = os.getenv("KEYWORDS")
    region = "eu-west-1"  # Fisso per Amazon Italia
    host = "webservices.amazon.it"

    # 3. Recupero prodotti
    try:
        print(f"🔍 Cerco prodotti per parola chiave: {keywords}")
        items = get_amazon_products(
            keywords=keywords,
            amazon_access_key=amazon_access_key,
            amazon_secret_key=amazon_secret_key,
            amazon_tag=amazon_tag,
            region=region,
            host=host
        )

        if not items:
            print("⚠ Nessun prodotto trovato.")
        else:
            print(f"✅ Trovati {len(items)} prodotti.")
            for i, item in enumerate(items, start=1):
                title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
                print(f"{i}. {title}")

    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
