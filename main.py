import os
import requests
from amazon_paapi import AmazonApi
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
import random

# === CONFIGURAZIONE VARIABILI D'AMBIENTE ===
access_key = os.environ.get("AMAZON_ACCESS_KEY")
secret_key = os.environ.get("AMAZON_SECRET_KEY")
partner_tag = "zamzam082-21"  # Tag affiliato fisso
country = os.environ.get("AMAZON_COUNTRY", "IT")
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
bitly_token = os.environ.get("BITLY_TOKEN")

# === CONTROLLI INIZIALI ===
if not all([access_key, secret_key, partner_tag, country, telegram_token, telegram_chat_id, bitly_token]):
    raise ValueError("❌ Manca una o più variabili d'ambiente nei Secrets di GitHub!")

# === FUNZIONE: ACCORCIARE LINK CON BITLY ===
def shorten_url(long_url):
    headers = {
        "Authorization": f"Bearer {bitly_token}",
        "Content-Type": "application/json"
    }
    data = {"long_url": long_url}
    try:
        response = requests.post("https://api-ssl.bitly.com/v4/shorten", json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("link")
        else:
            print(f"⚠️ Errore Bitly: {response.text}")
            return long_url
    except Exception as e:
        print(f"⚠️ Errore durante l'accorciamento: {e}")
        return long_url

# === INIZIALIZZO API AMAZON ===
amazon = AmazonApi(access_key, secret_key, partner_tag, country)

# === CATEGORIE / KEYWORDS ===
keywords = ["bambini", "neonati", "giocattoli", "mamme", "gravidanza", "passeggini", "seggiolini auto"]

# === CERCO OFFERTE ===
random.shuffle(keywords)  # Mischia per variare la ricerca
found_offer = None

for kw in keywords:
    try:
        products = amazon.search_products(keywords=kw, search_index="All", item_count=10)
        offers = []
        for p in products:
            if hasattr(p, "offers") and p.offers and hasattr(p.offers[0], "price") and p.offers[0].price.savings:
                savings_percentage = p.offers[0].price.savings.percentage
                if savings_percentage and savings_percentage >= 20:
                    offers.append(p)

        if offers:
            found_offer = random.choice(offers)
            break

    except Exception as e:
        print(f"⚠️ Errore ricerca per '{kw}': {e}")

# === INVIO SU TELEGRAM ===
bot = Bot(token=telegram_token)

if found_offer:
    title = found_offer.title
    price = found_offer.offers[0].price.display_amount if found_offer.offers else "Prezzo non disponibile"
    savings = found_offer.offers[0].price.savings.display_amount if found_offer.offers and found_offer.offers[0].price.savings else ""
    
    amazon_link = f"{found_offer.detail_page_url}&tag={partner_tag}"
    short_link = shorten_url(amazon_link)

    message_text = f"🎯 *{title}*\n💰 {price}  {f'(-{savings})' if savings else ''}"
    
    keyboard = [[InlineKeyboardButton("🛒 Acquista su Amazon", url=short_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        bot.send_message(chat_id=telegram_chat_id, text=message_text, reply_markup=reply_markup, parse_mode="Markdown")
        print("✅ Offerta pubblicata con successo!")
    except TelegramError as te:
        print(f"❌ Errore Telegram: {te}")

else:
    bot.send_message(chat_id=telegram_chat_id, text="⚠️ Oggi non ho trovato offerte superiori al 20% per la tua nicchia.")
    print("⚠️ Nessuna offerta trovata.")
