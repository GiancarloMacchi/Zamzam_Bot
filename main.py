import os
import time
import socket
from amazon_paapi import AmazonApi
import telegram

# Imposta un timeout globale per tutte le connessioni
socket.setdefaulttimeout(10)

# Variabili da ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
MIN_SAVE = int(os.getenv("MIN_SAVE", "10"))
ITEM_COUNT = 10

# Inizializza Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, country=AMAZON_COUNTRY)

# Inizializza bot Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def pick_deal():
    """Cerca tra le keywords e ritorna la prima offerta valida con immagine."""
    failed_count = 0  # contatore keyword fallite

    for kw in KEYWORDS:
        kw = kw.strip()
        if not kw:
            continue

        print(f"[INFO] Ricerca per keyword: {kw}")

        try:
            res = amazon.search_items(
                keywords=kw,
                item_count=ITEM_COUNT,
                min_saving_percent=MIN_SAVE
            )
        except Exception as e:
            failed_count += 1
            print(f"[WARN] errore o timeout ricerca '{kw}': {e} (Fallite: {failed_count}/{len(KEYWORDS)})")
            time.sleep(1.0)
            continue

        items = getattr(res, "items", []) or []

        for s in items:
            detail_url = getattr(s, "detail_page_url", None)
            asin = getattr(s, "asin", None) or getattr(s, "asin_value", None)

            if not detail_url and asin:
                detail_url = f"https://www.amazon.{AMAZON_COUNTRY.lower()}/dp/{asin}"

            if not detail_url:
                continue

            image_url = getattr(s, "image", None)
            if not image_url:
                continue

            title = getattr(s, "title", "Senza titolo")
            price = getattr(s, "price", None)

            return title, detail_url, image_url, price, failed_count

    return None, None, None, None, failed_count


def main():
    while True:
        title, url, image, price, failed_count = pick_deal()
        print(f"[INFO] Totale keyword fallite in questo giro: {failed_count}")

        if title and url:
            message = f"{title}\n{url}\nPrezzo: {price if price else 'N/D'}"
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        else:
            print("[INFO] Nessuna offerta trovata.")

        time.sleep(300)  # attesa di 5 minuti prima del prossimo giro


if __name__ == "__main__":
    main()
