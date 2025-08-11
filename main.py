import os
from amazon_api import cerca_prodotti
from telegram_bot import invia_messaggio

def esegui_bot():
    KEYWORDS = os.getenv("KEYWORDS", "offerte")
    ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))

    prodotti = cerca_prodotti(KEYWORDS, ITEM_COUNT)

    for prodotto in prodotti:
        titolo = prodotto.title
        prezzo = getattr(prodotto, "price", None)
        link = prodotto.detail_page_url

        messaggio = f"{titolo}\nPrezzo: {prezzo}\nLink: {link}"
        invia_messaggio(messaggio)
