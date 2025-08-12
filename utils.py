import math
from amazon_api import get_amazon_client, AMAZON_ASSOCIATE_TAG
from paapi5_python_sdk.models import SearchItemsRequest

def search_amazon_products(keywords, item_count=5, min_discount=0):
    """
    Cerca prodotti su Amazon usando PAAPI e filtra in base allo sconto minimo richiesto.
    """
    amazon = get_amazon_client()

    try:
        request = SearchItemsRequest(
            PartnerTag=AMAZON_ASSOCIATE_TAG,
            PartnerType="Associates",
            Keywords=keywords,
            ItemCount=item_count,
            Resources=[
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "DetailPageURL"
            ]
        )

        response = amazon.search_items(request)

    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []

    products = []
    try:
        if hasattr(response, "search_result") and response.search_result and response.search_result.items:
            for item in response.search_result.items:
                try:
                    title = getattr(item.item_info.title, "display_value", None)
                    url = getattr(item, "detail_page_url", None)
                    image_url = getattr(item.images.primary.medium, "url", None)

                    price_info = item.offers.listings[0].price if item.offers and item.offers.listings else None
                    saving_basis_info = (
                        item.offers.listings[0].saving_basis.price
                        if item.offers and item.offers.listings and item.offers.listings[0].saving_basis
                        else None
                    )

                    if price_info and saving_basis_info:
                        sale_price = price_info.amount
                        original_price = saving_basis_info.amount
                        discount = ((original_price - sale_price) / original_price) * 100
                    else:
                        discount = 0
                        original_price = None
                        sale_price = None

                    if discount >= min_discount and title and url and image_url:
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

    except Exception as e:
        print(f"Errore nel parsing dei risultati Amazon: {e}")

    return products
