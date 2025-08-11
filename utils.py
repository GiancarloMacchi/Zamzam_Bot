import os
import logging
from amazon_paapi import AmazonAPI
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Categorie rilevanti per bambini / genitori
RELEVANT_CATEGORIES = [
    "Bambini", "Neonati", "Genitori", "Scuola", "Libri per ragazzi",
    "Giocattoli", "Videogiochi", "Infanzia", "Prima infanzia", "Puericultura"
]

def category_matches(title, category):
    title_lower = title.lower()
    return any(cat.lower() in title_lower for cat in RELEVANT_CATEGORIES) or \
           any(cat.lower() in category.lower() for cat in RELEVANT_CATEGORIES)

def search_amazon_products(keyword, country, min_discount):
    amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, country)
    logging.info(f"🔍 Ricerca: {keyword} in {country}")

    try:
        products = amazon.search_items(keywords=keyword, item_count=int(os.getenv("ITEM_COUNT", 10)))
    except Exception as e:
        logging.error(f"Errore Amazon API: {e}")
        return []

    results = []
    for product in products:
        try:
            title = product.item_info.title.display_value if product.item_info.title else "Senza titolo"
            price = product.offers.listings[0].price.display_amount if product.offers.listings else "N/A"
            url = product.detail_page_url
            discount = 0
            category = product.item_info.classifications.binding.display_value if product.item_info.classifications and product.item_info.classifications.binding else ""

            # Calcolo sconto se disponibile
            if product.offers.listings and product.offers.listings[0].price.savings:
                discount = product.offers.listings[0].price.savings.percentage

            # Applica filtri SOLO per Amazon Italia
            if country == "IT":
                if discount >= min_discount and category_matches(title, category):
                    results.append({
                        "title": title,
                        "price": price,
                        "discount": discount,
                        "url": url
                    })
            else:
                # Per altri paesi nessun filtro
                results.append({
                    "title": title,
                    "price": price,
                    "discount": discount,
                    "url": url
                })

        except Exception as e:
            logging.warning(f"Errore parsing prodotto: {e}")

    logging.info(f"✅ {len(results)} prodotti trovati")
    return results

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            logging.error(f"Errore Telegram: {r.text}")
    except Exception as e:
        logging.error(f"Errore invio Telegram: {e}")
