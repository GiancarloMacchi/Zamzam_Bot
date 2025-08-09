import os
import time
import telegram
from amazon_paapi import AmazonAPI

# Configurazione da variabili d'ambiente
AMAZON_ACCESS_KEY = os.environ['AMAZON_ACCESS_KEY']
AMAZON_SECRET_KEY = os.environ['AMAZON_SECRET_KEY']
AMAZON_ASSOCIATE_TAG = os.environ['AMAZON_ASSOCIATE_TAG']
AMAZON_COUNTRY = os.environ['AMAZON_COUNTRY']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
KEYWORDS = os.environ['KEYWORDS'].split(',')
MIN_SAVE = int(os.environ['MIN_SAVE'])
ITEM_COUNT = 10  # Numero di item da cercare per keyword
TIMEOUT = 3  # Timeout Amazon API in secondi

# Inizializza API e bot
amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY, timeout=TIMEOUT)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def send_to_telegram(message, image_url=None):
    """Invia messaggio (e immagine opzionale) a Telegram."""
    if image_url:
        bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image_url, caption=message, parse_mode="HTML")
    else:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")

def pick_deal():
    """Cerca tra le keywords e ritorna la prima offerta valida con immagine."""
    failed_keywords = 0
    total_keywords = len(KEYWORDS)

    for kw in KEYWORDS:
        kw = kw.strip()
        try:
            res = amazon.search_items(keywords=kw, item_count=ITEM_COUNT, min_saving_percent=MIN_SAVE)
        except Exception as e:
            print(f"[WARN] errore ricerca '{kw}': {e}")
            failed_keywords += 1
            # Interrompi se più del 50% fallite
            if failed_keywords > total_keywords / 2:
                print("[STOP] Troppi errori di ricerca, interruzione anticipata.")
                return None, None
            if "throttling" in str(e).lower() or "rate limit" in str(e).lower():
                time.sleep(1)
            continue

        items = getattr(res, "items", []) or []
        if not items:
            failed_keywords += 1
            if failed_keywords > total_keywords / 2:
                print("[STOP] Troppi errori di ricerca, interruzione anticipata.")
                return None, None
            continue

        for s in items:
            detail_url = getattr(s, "detail_page_url", None)
            asin = getattr(s, "asin", None) or getattr(s, "asin_value", None)
            if not detail_url and asin:
                detail_url = f"https://www.amazon.{AMAZON_COUNTRY.lower()}/dp/{asin}"
            if not detail_url:
                continue

            image_url = None
            if hasattr(s, "images") and s.images:
                image_sets = getattr(s.images, "large", None) or getattr(s.images, "medium", None) or getattr(s.images, "small", None)
                if image_sets:
                    image_url = image_sets[0].url

            if image_url:
                title = getattr(s, "item_info", {}).get("title", {}).get("display_value", "Offerta Amazon")
                price = getattr(s, "offers", {}).get("listings", [{}])[0].get("price", {}).get("display_amount", "")
                message = f"<b>{title}</b>\n{price}\n<a href='{detail_url}'>Vedi offerta</a>"
                return message, image_url

    return None, None

if __name__ == "__main__":
    message, image_url = pick_deal()
    if message:
        send_to_telegram(message, image_url)
    else:
        print("[INFO] Nessuna offerta trovata.")
