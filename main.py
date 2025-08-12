import os
import logging
from dotenv import load_dotenv
import requests
import bitlyshortener
from amazon_paapi import AmazonApi

# =========================
# CONFIGURAZIONE LOGGING
# =========================
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO
)

# =========================
# CARICAMENTO VARIABILI
# =========================
load_dotenv()  # utile in locale, su GitHub Actions non serve ma non disturba

required_vars = [
    "AMAZON_ACCESS_KEY",
    "AMAZON_SECRET_KEY",
    "AMAZON_ASSOCIATE_TAG",
    "AMAZON_COUNTRY",
    "BITLY_TOKEN",
    "ITEM_COUNT",
    "KEYWORDS",
    "MIN_SAVE",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"❌ Variabili d'ambiente mancanti: {', '.join(missing_vars)}")

logging.info(f"🚀 Avvio bot Amazon - Partner tag: {os.getenv('AMAZON_ASSOCIATE_TAG')}")

# =========================
# FUNZIONI DI SUPPORTO
# =========================
def shorten_url(url):
    tokens = [os.getenv("BITLY_TOKEN")]
    shortener = bitlyshortener.Shortener(tokens=tokens)
    return shortener.shorten_urls([url])[0]

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    resp = requests.post(url, data=payload)
    if resp.status_code != 200:
        logging.error(f"Errore invio Telegram: {resp.text}")

# =========================
# AMAZON API
# =========================
amazon = AmazonApi(
    os.getenv("AMAZON_ACCESS_KEY"),
    os.getenv("AMAZON_SECRET_KEY"),
    os.getenv("AMAZON_ASSOCIATE_TAG"),
    os.getenv("AMAZON_COUNTRY")
)

keywords = [kw.strip() for kw in os.getenv("KEYWORDS").split(",")]
item_count = int(os.getenv("ITEM_COUNT"))
min_save = float(os.getenv("MIN_SAVE"))

for kw in keywords:
    logging.info(f"🔍 Ricerca per: {kw}")
    try:
        results = amazon.search_items(keywords=kw, item_count=item_count)
        for item in results:
            try:
                title = item.title
                url = shorten_url(item.detail_page_url)
                price = item.list_price and item.list_price.amount
                savings = item.saving_amount and item.saving_amount.amount

                if price and savings:
                    discount_percent = (savings / (price + savings)) * 100
                    if discount_percent >= min_save:
                        msg = f"<b>{title}</b>\n💰 Prezzo: {price}€\n💸 Sconto: {discount_percent:.0f}%\n🔗 {url}"
                        send_telegram_message(msg)
            except Exception as e:
                logging.error(f"Errore item: {e}")
    except Exception as e:
        logging.error(f"[ERRORE Amazon] ricerca '{kw}': {e}")

logging.info("✅ Bot completato")
