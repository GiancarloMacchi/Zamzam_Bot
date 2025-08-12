from amazon_api import get_amazon_client

def search_amazon_products(keywords, item_count=10):
    """
    Cerca prodotti su Amazon usando le API ufficiali.
    """
    amazon = get_amazon_client()
    try:
        products = amazon.search_items(keywords=keywords, item_count=item_count)
        return products
    except Exception as e:
        print(f"Errore durante la ricerca prodotti: {e}")
        return []

def format_product_info(product):
    """
    Restituisce una stringa formattata con le informazioni essenziali di un prodotto.
    """
    title = getattr(product, "title", "Titolo non disponibile")
    url = getattr(product, "url", "URL non disponibile")
    price = getattr(product, "price", "Prezzo non disponibile")
    return f"{title}\nPrezzo: {price}\nLink: {url}"
