import os
import random
from utils import search_amazon_products
from telegram_bot import get_telegram_client, send_telegram_photo

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

    title = product.get("title", "Offerta Amazon")
    original_price = product.get("original_price", "-")
    sale_price = product.get("sale_price", "-")
    discount = product.get("discount", "-")
    url = product.get("url", "#")

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
    """
    Avvia la ricerca dei prodotti e invia le offerte su Telegram.
    """
    KEYWORDS = os.getenv("KEYWORDS", "offerte del giorno")
    ITEM_COUNT = int(os.getenv("ITEM_COUNT", 6))
    MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", 20))  # sconto minimo %

    print(f"🔍 Ricerca prodotti Amazon per: {KEYWORDS} | Sconto minimo: {MIN_DISCOUNT}%")
    prodotti = search_amazon_products(KEYWORDS, ITEM_COUNT, MIN_DISCOUNT)

    if not prodotti:
        print("⚠ Nessun prodotto trovato che soddisfi i criteri.")
        return

    try:
        bot = get_telegram_client()
        for prodotto in prodotti:
            if not prodotto.get("image_url"):
                print(f"⏭ Prodotto senza immagine: {prodotto.get('title')}")
                continue

            post_message = create_telegram_post(prodotto)
            send_telegram_photo(bot, prodotto["image_url"], post_message)
            print(f"✅ Post inviato per: {prodotto.get('title')}")
    except Exception as e:
        print(f"❌ Errore nell'invio a Telegram: {e}")

if __name__ == "__main__":
    esegui_bot()
