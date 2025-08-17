import logging
import random

def search_amazon(keyword):
    # Simulazione prodotti per DRY_RUN
    logging.info(f"[DRY RUN] Simulazione ricerca Amazon per keyword: {keyword}")
    products = []
    for i in range(1, 6):  # 5 prodotti per keyword
        products.append({
            "title": f"{keyword} Prodotto {i}",
            "url": f"https://www.amazon.***/dp/EXAMPLE{i}?tag=iltuotag-21",
            "price": f"{random.randint(10,100)},99€",
            "image_url": f"https://via.placeholder.com/150?text={keyword}+{i}",
            "description": f"Breve descrizione per {keyword} Prodotto {i}"
        })
    return products
