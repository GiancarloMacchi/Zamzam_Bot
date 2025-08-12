import os
import logging
from amazon_paapi import AmazonApi
from telegram import Bot
from datetime import datetime

# === CONFIG ===
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", "10"))
MIN_SAVE = int(os.getenv("MIN_SAVE", "10"))

# Parole whitelist
WHITELIST_KEYWORDS = [
    "infanzia", "mamma", "bimbo", "bambino", "bambina",
    "papà", "libri bambini", "vestiti bambino", "premaman",
    "scuola", "asilo", "asilo nido", "colori", "pastelli",
    "regalo", "piscina", "costume", "ciabatte",
    "ragazzo", "ragazza", "adolescente"
]

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

def main():
    logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

    amazon = AmazonApi(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    for kw in WHITELIST_KEYWORDS:
        logging.info(f"🔍 Ricerca per: {kw}")
        try:
            results = amazon.search_items(
                keywords=kw,
                item_count=ITEM_COUNT  # ✅ Passato SOLO una volta
            )
            found_count = len(results.items) if results and results.items else 0
            logging.info(f"📦 {found_count} risultati trovati per '{kw}'")
        except Exception as e:
            logging.error(f"[ERRORE Amazon] ricerca '{kw}': {e}")
            continue

        for item in results.items:
            try:
                title = item.item_info.title.display_value
                price_info = item.offers.listings[0].price
                saving_info = item.offers.listings[0].saving_basis

                if saving_info and saving_info.amount > 0:
                    save_percent = (saving_info.amount / saving_info.value) * 100
                    if save_percent >= MIN_SAVE:
                        msg = f"💥 {kw.capitalize()} in offerta!\n" \
                              f"{title}\n" \
                              f"💶 {price_info.display_amount} (-{int(save_percent)}%)\n" \
                              f"🔗 {item.detail_page_url}"
                        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            except Exception as e:
                logging.error(f"[ERRORE parsing] {e}")

    logging.info("✅ Bot completato")

if __name__ == "__main__":
    main()
