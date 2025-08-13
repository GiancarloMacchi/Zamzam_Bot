import os
import json
import random
import time
import logging
from amazon_paapi.api import AmazonAPI  # Import corretto
from telegram_api import TelegramBot

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Credenziali Amazon dal Repository Secrets
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Credenziali Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Parametri di ricerca
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))

# Lista di keyword
KEYWORDS = json.loads(os.getenv("KEYWORDS", '["infanzia", "giochi", "giocattoli", "mamma", "papà", "bimbo", "bimba", "bambino", "bambina", "scuola", "asilo", "asilo nido", "pastelli", "colori"]'))

# File per tracciare articoli già postati
SEEN_FILE = ".seen_items.json"

# Caricamento articoli già visti
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        try:
            seen_items = json.load(f)
        except json.JSONDecodeError:
            seen_items = []
else:
    seen_items = []

# Caricamento frasi da phrases.json
with open("phrases.json", "r", encoding="utf-8") as f:
    phrases = json.load(f)

# Avvio bot
logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")

amazon_api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

# Ciclo sulle keyword
for keyword in KEYWORDS:
    logging.info(f"🔍 Ricerca per: {keyword}")
    results = amazon_api.search_items(keywords=keyword, item_count=ITEM_COUNT)

    for item in results.items:
        try:
            asin = item.asin
            title = item.item_info.title.display_value
            link = item.detail_page_url
            price = getattr(item.offers.listings[0].price, 'display_amount', None)
            savings = getattr(item.offers.listings[0].saving_basis, 'display_amount', None)
            pct_saving = getattr(item.offers.listings[0].price.savings, 'percentage', 0)
            image_url = item.images.primary.large.url

            if pct_saving < MIN_SAVE:
                continue
            if asin in seen_items:
                continue

            # Frase ironica random per la keyword
            phrase_list = phrases.get(keyword, phrases.get("default", []))
            chosen_phrase = random.choice(phrase_list) if phrase_list else ""

            message = f"{chosen_phrase}\n\n📌 {title}\n💰 {price} (-{pct_saving}%)\n\n🔗 {link}"

            telegram_bot.send_message(message, image_url=image_url)
            seen_items.append(asin)

            # Delay random tra 30 e 90 secondi
            time.sleep(random.randint(30, 90))

        except Exception as e:
            logging.error(f"Errore con l'articolo {keyword}: {e}")

# Salvataggio articoli visti
with open(SEEN_FILE, "w") as f:
    json.dump(seen_items, f)

logging.info("✅ Bot completato")
