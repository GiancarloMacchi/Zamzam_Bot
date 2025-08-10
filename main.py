import os
import logging
from utils import search_products, send_telegram_message, shorten_url

logging.basicConfig(level=logging.INFO, format="***%(asctime)s*** - %(levelname)s - %(message)s")

MIN_SAVE = int(os.getenv("MIN_SAVE", 20))  # Sconto minimo in %
KEYWORDS = os.getenv("KEYWORDS", "infanzia,bambini,genitori,scuola").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))

def category_matches(categories):
    if not categories:
        return False
    categories_lower = [c.lower() for c in categories]
    return any(keyword.strip().lower() in c for keyword in KEYWORDS for c in categories_lower)

def main():
    logging.info("🔍 Avvio ricerca prodotti Amazon...")
    try:
        products = search_products()
    except Exception as e:
        logging.error(f"Errore nella ricerca prodotti: {e}")
        return

    for product in products:
        try:
            title = product.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
            offers = product.get("Offers")
            if not offers:
                logging.info(f"↪️ Nessuna offerta per '{title}', salto...")
                continue

            saving_basis = offers.get("Listings", [])[0].get("Price", {}).get("Savings", {}).get("Percentage", 0)
            if saving_basis < MIN_SAVE:
                logging.info(f"↪️ Sconto {saving_basis}% inferiore al minimo per '{title}', salto...")
                continue

            categories = [b.get("DisplayName", "") for b in product.get("BrowseNodeInfo", {}).get("BrowseNodes", [])]
            if not category_matches(categories):
                logging.info(f"↪️ Categoria non rilevante per '{title}', salto...")
                continue

            url = product.get("DetailPageURL", "")
            short_url = shorten_url(url)

            message = f"🎯 *{title}*\n💰 Sconto: {saving_basis}%\n🔗 [Vedi su Amazon]({short_url})"
            send_telegram_message(message)
            logging.info(f"✅ Inviato: {title}")

        except Exception as e:
            logging.error(f"Errore con il prodotto '{title}': {e}")
            continue

if __name__ == "__main__":
    main()
