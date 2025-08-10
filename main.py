import os
import logging
from amazon_paapi import AmazonApi
from utils import send_telegram_message, get_discount_percentage

# Logging
logging.basicConfig(level=logging.INFO)

# Credenziali Amazon API da secrets
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")

# Telegram
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Categorie target
CATEGORIES = [
    "Baby",
    "Toys",
    "Kids",
    "Children",
    "School",
    "Motherhood",
    "Parenting"
]

# Inizializza API
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

def main():
    for category in CATEGORIES:
        try:
            logging.info(f"🔍 Cerco offerte nella categoria: {category}")
            products = amazon.search_items(keywords=category, item_count=10)
            
            for product in products:
                try:
                    if not hasattr(product, "offers") or not product.offers:
                        continue

                    discount = get_discount_percentage(product)
                    if discount is None or discount < 20:
                        continue

                    message = f"🛍 *{product.title}*\n💰 Prezzo: {product.price}\n📉 Sconto: {discount}%\n🔗 [Vedi Offerta]({product.url})"
                    send_telegram_message(message, TELEGRAM_CHAT_ID)

                except Exception as e:
                    logging.error(f"Errore elaborando un prodotto: {e}")
                    continue  # Continua con il prossimo prodotto

        except Exception as e:
            logging.error(f"Errore nella categoria {category}: {e}")
            continue  # Continua con la prossima categoria

if __name__ == "__main__":
    main()
