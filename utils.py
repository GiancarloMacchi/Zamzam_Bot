from amazon_api import get_amazon_client
import math

def search_amazon_products(keywords, item_count=5, min_discount=0):
    """
    Cerca prodotti su Amazon usando le API ufficiali e filtra per sconto.
    """
    amazon = get_amazon_client()
    try:
        results = amazon.search_items(
            Keywords=keywords,
            ItemCount=item_count,
            Resources=["Images.Primary.Medium", "ItemInfo.Title", "Offers.Listings.Price", "Offers.Listings.SavingBasis"]
        )
    except Exception as e:
        print(f"Errore nella ricerca Amazon: {e}")
        return []

    products = []
    for item in results.SearchResult.Items:
        try:
            # Estrazione dei dati
            title = item.ItemInfo.Title.DisplayValue
            url = item.DetailPageURL
            image_url = item.Images.Primary.Medium.URL
            
            # Gestione dei prezzi e calcolo dello sconto
            saving_basis = item.Offers.Listings[0].SavingBasis.Price.Amount if item.Offers.Listings[0].SavingBasis else None
            sale_price = item.Offers.Listings[0].Price.Amount if item.Offers.Listings[0].Price else None

            if saving_basis and sale_price:
                discount = ((saving_basis - sale_price) / saving_basis) * 100
                if discount >= min_discount:
                    products.append({
                        "title": title,
                        "url": url,
                        "image_url": image_url,
                        "original_price": f"{saving_basis:.2f} €",
                        "sale_price": f"{sale_price:.2f} €",
                        "discount": f"{math.floor(discount)}%",
                        "discount_raw": discount
                    })
        except (AttributeError, TypeError) as e:
            # Ignora prodotti con dati incompleti
            print(f"Skipping product due to missing data: {e}")
            continue

    return products
