import math
from amazon_api import get_amazon_client

def search_amazon_products(keywords, item_count=5, min_discount=0):
    """
    Cerca prodotti su Amazon e filtra in base allo sconto minimo richiesto.
    """
    amazon = get_amazon_client()

    try:
        results = amazon.search_products(
            keywords=keywords,
            search_index="All",
            item_count=item_count
        )
    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []

    products = []
    for item in results:
        try:
            title = item.title
            url = item.detail_page_url
            image_url = item.images.large or item.images.medium or item.images.small

            original_price = item.list_price if item.list_price else None
            sale_price = item.offer_price if item.offer_price else None

            discount = 0
            if original_price and sale_price and original_price > 0:
                discount = ((original_price - sale_price) / original_price) * 100

            if discount >= min_discount:
                products.append({
                    "title": title,
                    "url": url,
                    "image_url": image_url,
                    "original_price": f"{original_price:.2f} €" if original_price else "-",
                    "sale_price": f"{sale_price:.2f} €" if sale_price else "-",
                    "discount": f"{math.floor(discount)}%",
                    "discount_raw": discount
                })
        except Exception as e:
            print(f"Prodotto ignorato per dati incompleti: {e}")
            continue

    return products
