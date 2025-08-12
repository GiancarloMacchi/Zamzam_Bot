import os
from utils import search_amazon_products, format_product_info

KEYWORDS = os.getenv("KEYWORDS", "libri")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))

def esegui_bot():
    """
    Esegue la ricerca e stampa i risultati.
    """
    print(f"🔍 Ricerca di '{KEYWORDS}' su Amazon...")
    prodotti = search_amazon_products(KEYWORDS, ITEM_COUNT)

    if not prodotti:
        print("Nessun prodotto trovato.")
        return

    for p in prodotti:
        print(format_product_info(p))
