import os
import json
import random
from amazon_paapi import AmazonAPI
import telegram
from telegram.constants import ParseMode

# Legge le variabili d'ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = json.loads(os.getenv("KEYWORDS", '["infanzia"]'))

# Carica il phrases.json
with open("phrases.json", "r", encoding="utf-8") as f:
    phrases = json.load(f)

def get_phrase(category):
    """Restituisce una frase casuale per la categoria specificata."""
    category = category.strip().lower()
    if category not in phrases:
        category = "default"
    if category not in phrases:
        return "💥 Offerta imperdibile!"
    return random.choice(phrases[category])

# Inizializza Amazon API
amazon_api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

# Inizializza Telegram bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

for keyword in KEYWORDS:
    print(f"[INFO] 🔍 Ricerca per: {keyword}")
    results = amazon_api.search_items(
        keywords=keyword,
        item_count=ITEM_COUNT,
        min_saving_percent=MIN_SAVE
    )

    for item in results:
        title = item.item_info.title.display_value if item.item_info.title else "Senza titolo"
        price = item.offers.listings[0].price.display_amount if item.offers and item.offers.listings else "N/A"
        saving = item.offers.listings[0].saving_basis.amount if item.offers and item.offers.listings and item.offers.listings[0].saving_basis else 0
        url = item.detail_page_url
        image = item.images.primary.large.url if item.images and item.images.primary and item.images.primary.large else None

        # Recupera frase casuale per la categoria
        phrase = get_phrase(keyword)

        message = f"{phrase}\n\n📦 <b>{title}</b>\n💲 {price} (-{saving}%)\n🔗 {url}"

        if image:
            bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image, caption=message, parse_mode=ParseMode.HTML)
        else:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
