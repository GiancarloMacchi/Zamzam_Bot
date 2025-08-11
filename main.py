from amazon_paapi import AmazonApi
import os

def esegui_bot():
    amazon = AmazonApi(
        os.getenv("AMAZON_ACCESS_KEY"),
        os.getenv("AMAZON_SECRET_KEY"),
        os.getenv("AMAZON_ASSOCIATE_TAG"),
        os.getenv("AMAZON_COUNTRY")
    )

    # Esegui ricerca
    result = amazon.search_items(
        keywords=os.getenv("KEYWORDS"),
        item_count=int(os.getenv("ITEM_COUNT"))
    )

    # Accedi correttamente alla lista di prodotti
    if hasattr(result, "search_result") and hasattr(result.search_result, "items"):
        prodotti = result.search_result.items
    elif hasattr(result, "items"):  
        prodotti = result.items
    else:
        prodotti = []

    # Itera sui prodotti
    for prodotto in prodotti:
        titolo = prodotto.item_info.title.display_value if prodotto.item_info and prodotto.item_info.title else "Titolo non disponibile"
        prezzo = prodotto.offers.listings[0].price.display_amount if prodotto.offers and prodotto.offers.listings else "Prezzo non disponibile"
        url = prodotto.detail_page_url if prodotto.detail_page_url else "URL non disponibile"

        print(f"{titolo} - {prezzo} - {url}")
