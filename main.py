import os
import logging
from utils import search_products, send_telegram_message, get_discount_percentage

logging.basicConfig(
    level=logging.INFO,
    format="***%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

# Legge variabili ambiente
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))

# Categorie consentite (parole chiave in lowercase)
ALLOWED_CATEGORIES = [
    "infanzia",
    "bambini",
    "genitori",
    "scuola",
    "neonati",
    "maternità",
    "puericultura",
    "giocattoli educativi"
]

def is_category_allowed(categories):
    """Controlla se almeno una categoria è ammessa"""
    if not categories:
        return False
    categories_lower = [c.lower() for c in categories]
    return any(allowed in c for c in categories_lower for allowed in ALLOWED_CATEGORIES)

def main():
    logging.info("🔍 Avvio ricerca prodotti Amazon...")

    try:
        products = search_products()
    except Exception as e:
        logging.error(f"Errore durante la ricerca prodotti: {e}")
        return

    if not products:
        logging.info("Nessun prodotto trovato.")
        return

    for product in products:
        try:
            title = product.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
            offers = product.get("Offers")
            categories = product.get("BrowseNodeInfo", {}).get("BrowseNodes", [])

            # Estrai nomi categorie
            category_names = []
            for c in categories:
                name = c.get("DisplayName")
                if name:
                    category_names.append(name)

            # Filtra categorie
            if not is_category_allowed(category_names):
                logging.info(f"❌ Categoria non ammessa per '{title}', salto...")
                continue

            if not offers:
                logging.info(f"Nessuna offerta per '{title}', salto...")
                continue

            # Calcola sconto
            discount = get_discount_percentage(product)
            if discount < MIN_SAVE:
                logging.info(f"Sconto {discount}% inferiore al minimo per '{title}', salto...")
                continue

            # Prepara messaggio
            url = product.get("DetailPageURL", "#")
            message = f"🎯 *{title}*\n💰 Sconto: *{discount}%*\n🔗 [Acquista qui]({url})"

            # Invia messaggio singolo
            send_telegram_message(message)

        except Exception as e:
            logging.error(f"Errore con prodotto '{product.get('ASIN', 'sconosciuto')}': {e}")
            continue

if __name__ == "__main__":
    main()
