import logging
import os
from amazon_api import get_amazon_products
from utils import setup_logger, send_telegram_message

KEYWORDS = os.getenv("KEYWORDS", "bambini,infanzia,mamme").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))  # sconto minimo in %
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

def format_product_message(product):
    """Formatta i dati di un prodotto in testo HTML per Telegram."""
    title = product.item_info.title.display_value if hasattr(product, 'item_info') else "Prodotto senza titolo"
    url = product.detail_page_url if hasattr(product, 'detail_page_url') else "#"
    price = None
    try:
        price = product.offers.listings[0].price.display_amount
    except:
        price = "Prezzo non disponibile"

    return f"<b>{title}</b>\n💰 {price}\n🔗 <a href='{url}'>Acquista ora</a>"

def esegui():
    setup_logger()
    total_sent = 0

    for keyword in KEYWORDS:
        logging.info(f"🔍 Searching '{keyword}' on Amazon.it")
        products = get_amazon_products(keyword.strip(), ITEM_COUNT)

        for product in products:
            try:
                message = format_product_message(product)
                if send_telegram_message(message):
                    total_sent += 1
            except Exception as e:
                logging.error(f"Errore durante l'elaborazione del prodotto: {e}")

    logging.info(f"📦 Invio completato ✅ - Totale messaggi inviati: {total_sent}")

if __name__ == "__main__":
    esegui()
    if not RUN_ONCE:
        logging.info("⏳ RUN_ONCE è disattivato — il loop continuo non è implementato in questa versione.")
