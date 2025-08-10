import logging
import os
import random
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from amazon_paapi import AmazonApi
from deep_translator import GoogleTranslator

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# Credenziali Amazon PA-API
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG")

# Token del bot Telegram e ID del canale
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Configurazione Amazon API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_PARTNER_TAG, "IT")

# Keywords per ricerca (ampliate)
KEYWORDS = [
    "mamma", "neonato", "passeggino", "libri bambini", "gravidanza", "scuola",
    "giochi bambini", "seggiolino auto", "abbigliamento neonato", "latte in polvere",
    "biberon", "fasciatoio", "pannolini", "culla", "lettino"
]

# Numero massimo di prodotti per keyword
ITEM_COUNT = 20
MIN_DISCOUNT = 20  # sconto minimo in percentuale

# Bot Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def get_discount_percentage(item):
    try:
        list_price = float(item["Offers"]["Listings"][0]["Price"]["Savings"]["Percentage"])
        return list_price
    except:
        return 0

def generate_affiliate_link(url):
    # L'API Amazon restituisce già link con partner tag, ma possiamo accorciarli con amzn.to se vogliamo
    return url

def create_custom_message(title):
    templates = [
        f"\"Perfetto per i più piccoli: {title}! Un'occasione da non perdere 😍\"",
        f"\"Con {title} la vita diventa più semplice! Approfitta dello sconto 🤩\"",
        f"\"Il nostro piccolo ha adorato {title}, e il tuo? 🍼💖\"",
        f"\"Un regalo ideale: {title}. Non lasciartelo scappare 🎁\""
    ]
    return random.choice(templates)

def search_and_post():
    for keyword in KEYWORDS:
        logging.info(f"🔍 Cerco: {keyword}")
        try:
            results = amazon.search_items(
                keywords=keyword,
                item_count=ITEM_COUNT,
                resources=[
                    "Images.Primary.Medium",
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis",
                    "Offers.Listings.Price.Savings"
                ]
            )

            offers_found = False

            for item in results["SearchResult"]["Items"]:
                discount = get_discount_percentage(item)
                if discount >= MIN_DISCOUNT:
                    offers_found = True

                    title = item["ItemInfo"]["Title"]["DisplayValue"]
                    url = item["Offers"]["Listings"][0]["MerchantInfo"]["MerchantName"]
                    image_url = item["Images"]["Primary"]["Medium"]["URL"]
                    price = item["Offers"]["Listings"][0]["Price"]["DisplayAmount"]
                    affiliate_link = generate_affiliate_link(item["DetailPageURL"])

                    custom_message = create_custom_message(title)

                    # Pulsante con link affiliato
                    button = [[InlineKeyboardButton("🛒 Acquista ora", url=affiliate_link)]]
                    reply_markup = InlineKeyboardMarkup(button)

                    message_text = f"**{title}** - SCONTO {discount}%\n\n💰 {price}\n\n{custom_message}"

                    bot.send_photo(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        photo=image_url,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )

            if not offers_found:
                logging.info(f"Nessuna offerta trovata per '{keyword}'.")

        except Exception as e:
            logging.error(f"Errore durante la ricerca per '{keyword}': {e}")

if __name__ == "__main__":
    search_and_post()
