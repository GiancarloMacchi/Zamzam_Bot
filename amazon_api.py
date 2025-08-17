import requests
import logging
from config import load_config

config = load_config()
ITEM_COUNT = int(config["ITEM_COUNT"])
AMAZON_COUNTRY = config["AMAZON_COUNTRY"]
AMAZON_ACCESS_KEY = config["AMAZON_ACCESS_KEY"]
AMAZON_SECRET_KEY = config["AMAZON_SECRET_KEY"]
AMAZON_ASSOCIATE_TAG = config["AMAZON_ASSOCIATE_TAG"]

# Endpoint PA-API 5.0
ENDPOINT = f"https://webservices.amazon.{AMAZON_COUNTRY}/paapi5/searchitems"

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json"
}

def search_amazon(keyword):
    """
    Cerca prodotti reali su Amazon via PA-API 5.0
    Restituisce lista di dizionari: title, url, price, image_url
    """
    payload = {
        "Keywords": keyword,
        "Resources": [
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price"
        ],
        "PartnerTag": AMAZON_ASSOCIATE_TAG,
        "PartnerType": "Associates",
        "Marketplace": f"www.amazon.{AMAZON_COUNTRY}",
        "ItemCount": ITEM_COUNT
    }

    try:
        # Nota: la firma AWS v4 deve essere gestita, qui per test DRY_RUN simuliamo la chiamata
        if config.get("DRY_RUN", "True") == "True":
            logging.info(f"[DRY RUN] Simulazione ricerca Amazon per keyword: {keyword}")
            products = []
            for i in range(1, ITEM_COUNT + 1):
                products.append({
                    "title": f"{keyword} Prodotto {i}",
                    "url": f"https://www.amazon.{AMAZON_COUNTRY}/dp/EXAMPLE{i}",
                    "price": f"{10*i},99€",
                    "image_url": f"https://via.placeholder.com/150?text={keyword}+{i}"
                })
            return products

        response = requests.post(ENDPOINT, json=payload, headers=HEADERS, auth=(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY))
        response.raise_for_status()
        data = response.json()

        products = []
        for item in data.get("Items", [])[:ITEM_COUNT]:
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue")
            url = item.get("DetailPageURL")
            price = None
            offers = item.get("Offers", {}).get("Listings", [])
            if offers:
                price = offers[0].get("Price", {}).get("DisplayAmount")
            image_url = item.get("Images", {}).get("Primary", {}).get("Medium", {}).get("URL")
            products.append({
                "title": title or "N/D",
                "url": url or "#",
                "price": price or "N/D",
                "image_url": image_url or None
            })
        return products
    except Exception as e:
        logging.error(f"Errore API Amazon: {e}")
        return []
