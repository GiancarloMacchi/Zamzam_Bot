import os
from amazon_paapi import AmazonApi
from bitlyshortener import Shortener
from telegram import Bot
from dotenv import load_dotenv

# Carica variabili da .env o Repository secrets di GitHub
load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
KEYWORDS = os.getenv("KEYWORDS", "iPhone")
MIN_SAVE = float(os.getenv("MIN_SAVE", 0))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza Amazon API
amazon = AmazonApi(
    AMAZON_ACCESS_KEY,
    AMAZON_SECRET_KEY,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_COUNTRY
)

# Inizializza Bitly
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

# Inizializza Bot Telegram
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def cerca_offerte():
    print(f"🔍 Ricerca: {KEYWORDS}")
    products = amazon.search_items(
        keywords=KEYWORDS,
        item_count=ITEM_COUNT
    )

    for product in products:
        try:
            title = product.item_info.title.display_value
            price = float(product.offers.listings[0].price.amount)
            saving = product.offers.listings[0].price.savings.amount \
                if product.offers.listings[0].price.savings else 0
            saving_percentage = (saving / (price + saving) * 100) if saving > 0 else 0
            url = product.detail_page_url

            # Filtra in base al MIN_SAVE
            if saving_percentage >= MIN_SAVE:
                short_url = shortener.shorten_urls([url])[0]
                messaggio = f"📦 {title}\n💰 Prezzo: {price}€\n💸 Sconto: {saving_percentage:.1f}%\n🔗 {short_url}"
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio)

        except Exception as e:
            print(f"Errore nel prodotto: {e}")

if __name__ == "__main__":
    cerca_offerte()
