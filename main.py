import os
import logging
from amazon_paapi import AmazonApi
from utils import shorten_url, send_telegram_message

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# Carica le variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
KEYWORDS = os.getenv("KEYWORDS", "bambini, infanzia, scuola").split(",")
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))

# Inizializza Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

def main():
    for keyword in KEYWORDS:
        keyword = keyword.strip()
        logging.info(f"🔍 Ricerca per keyword: {keyword}")

        try:
            products = amazon.search_items(keywords=keyword, item_count=ITEM_COUNT)
        except Exception as e:
            logging.error(f"Errore durante la ricerca per '{keyword}': {e}")
            continue

        for product in products:
            try:
                # Salta se non ha Offers
                if not hasattr(product, "offers") or not product.offers:
                    logging.warning(f"Prodotto senza Offers: {product.item_info.title.display_value}")
                    continue

                offer = product.offers.listings[0]
                price_info = offer.price
                if not price_info or not price_info.savings:
                    logging.warning(f"Nessun dato sullo sconto per: {product.item_info.title.display_value}")
                    continue

                discount = int(price_info.savings.percentage)
                if discount < MIN_SAVE:
                    continue

                title = product.item_info.title.display_value
                image_url = product.images.primary.large.url if product.images and product.images.primary else None
                product_url = shorten_url(product.detail_page_url, BITLY_TOKEN)

                message = (
                    f"📌 *{title}*\n"
                    f"💰 Prezzo: {price_info.display_amount}\n"
                    f"💸 Sconto: -{discount}%\n"
                    f"🔗 [Acquista qui]({product_url})"
                )

                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, image_url)

            except Exception as e:
                logging.error(f"Errore prodotto: {e}")
                continue

    logging.info("✅ Invio completato")

if __name__ == "__main__":
    main()
