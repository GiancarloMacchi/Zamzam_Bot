import os
import logging
import random
from dotenv import load_dotenv
from telegram import Bot
from amazon_paapi import AmazonApi

# Carica variabili d'ambiente
load_dotenv()

# Configurazione logging
logging.basicConfig(level=logging.INFO, format="***%(asctime)s - %(levelname)s - %(message)s")

# Credenziali Amazon PA-API
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOC_TAG = os.getenv("AMAZON_ASSOC_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")  # es: 'IT'

# Credenziali Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Inizializza API
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, AMAZON_COUNTRY)
bot = Bot(token=TELEGRAM_TOKEN)

# Categorie di ricerca generiche per il settore bambini/genitori
SEARCH_TERMS = [
    "bambini",
    "giocattoli",
    "giochi",
    "abbigliamento bambini",
    "abbigliamento neonato",
    "abbigliamento premaman",
    "mamme",
    "prima infanzia",
    "libri bambini"
]

MIN_DISCOUNT = 20  # percentuale minima di sconto

def get_discount_percentage(item):
    """Calcola la percentuale di sconto se disponibile"""
    try:
        price = item.offers.listings[0].price.amount
        saving_basis = item.offers.listings[0].saving_basis.amount
        discount = ((saving_basis - price) / saving_basis) * 100
        return round(discount, 2)
    except (AttributeError, IndexError, TypeError):
        return 0

def search_deals():
    """Cerca offerte con almeno MIN_DISCOUNT% di sconto"""
    found_items = []

    for term in SEARCH_TERMS:
        logging.info(f"🔍 Cerco: {term}")
        try:
            items = amazon.search_items(
                keywords=term,
                search_index="All",
                resources=[
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis",
                    "Images.Primary.Medium"
                ],
                item_count=10
            )

            # Filtro per sconto minimo
            for item in items:
                discount = get_discount_percentage(item)
                if discount >= MIN_DISCOUNT:
                    found_items.append(item)

        except Exception as e:
            logging.warning(f"Errore durante la ricerca di '{term}': {e}")

    return found_items

def format_message(item):
    """Crea il messaggio Telegram con titolo, prezzo, sconto e link"""
    title = item.item_info.title.display_value
    price = item.offers.listings[0].price.display_amount
    discount = get_discount_percentage(item)
    url = item.detail_page_url
    image = item.images.primary.medium.url

    return f"🎁 <b>{title}</b>\n💰 Prezzo: {price} (-{discount}%)\n🔗 <a href='{url}'>Vedi su Amazon</a>\n\n{image}"

def main():
    deals = search_deals()

    if not deals:
        logging.info(f"Nessuna offerta trovata con sconto ≥ {MIN_DISCOUNT}%.")
        bot.send_message(chat_id=TELEGRAM_CHANNEL_ID,
                         text=f"⚠ Nessuna offerta trovata con sconto ≥ {MIN_DISCOUNT}%.",
                         parse_mode="HTML")
        return

    # Scegli un'offerta casuale
    deal = random.choice(deals)
    message = format_message(deal)

    # Pubblica sul canale
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode="HTML")

if __name__ == "__main__":
    main()
