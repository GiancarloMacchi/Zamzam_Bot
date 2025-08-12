from utils import search_amazon_products
import os

KEYWORDS = os.getenv("KEYWORDS", "smartphone")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

def esegui_bot():
    print(f"Ricerca prodotti Amazon per: {KEYWORDS}")
    prodotti = search_amazon_products(KEYWORDS, ITEM_COUNT, MIN_SAVE)
    for prodotto in prodotti:
        print(f"- {prodotto.title} | {prodotto.detail_page_url}")
