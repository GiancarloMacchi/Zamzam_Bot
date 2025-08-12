from utils import search_amazon_products
from telegram_bot import get_telegram_client, send_telegram_photo
import os
import random

def create_telegram_post(product):
    """
    Crea un testo accattivante per il post di Telegram.
    """
    frasi_casuali = [
        "Affrettati, l'offerta è pazzesca! 🏃‍♀️💨",
        "Non fartelo scappare, è un affare d'oro! ✨",
        "Prezzo bomba, risparmio assicurato! 💣",
        "Wow! Lo sconto è esagerato! 🤩"
    ]

    title = product['title']
    original_price = product['original_price']
    sale_price = product['sale_price']
    discount = product['discount']
    url = product['url']

    message = (
        f"<b>{title}</b>\n\n"
        f"Prezzo di listino: <s>{original_price}</s>\n"
        f"<b>Prezzo offerta: {sale_price}</b>\n"
        f"Risparmi il {discount}!\n\n"
        f"{random.choice(frasi_casuali)}\n\n"
        f"➡️ <a href='{url}'>Clicca qui per acquistarlo!</a>"
    )

    return message

def esegui_bot():
    KEYWORDS = os.getenv("KEYWORDS", "offerte del giorno")
    ITEM_COUNT = int(os.getenv("ITEM_COUNT", 6))
    MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", 20)) # Valore minimo di sconto per l'offerta

    print(f"Ricerca prodotti Amazon per: {KEYWORDS} con sconto minimo del {MIN_DISCOUNT}%")
    prodotti = search_amazon_products(KEYWORDS, ITEM_COUNT, MIN_DISCOUNT)
    
    if not prodotti:
        print("Nessun prodotto trovato che soddisfi i criteri.")
        return

    try:
        bot = get_telegram_client()
        for prodotto in prodotti:
            post_message = create_telegram_post(prodotto)
            send_telegram_photo(bot, prodotto['image_url'], post_message)
            print(f"Post inviato per: {prodotto['title']}")
    except Exception as e:
        print(f"Errore nell'invio a Telegram: {e}")

if __name__ == "__main__":
    esegui_bot()
