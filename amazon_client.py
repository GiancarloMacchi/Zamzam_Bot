import logging
import random

class AmazonClient:
    def __init__(self, access_key, secret_key, associate_tag, country, keywords, min_save, item_count):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.country = country
        self.keywords = keywords
        self.min_save = min_save
        self.item_count = item_count

    def search_items(self, keyword):
        """Simula una ricerca Amazon restituendo prodotti finti."""
        logging.info(f"🔍 [MOCK] Cerco prodotti per: {keyword}")

        results = []
        for i in range(self.item_count):
            discount = random.randint(self.min_save, 50)
            price = round(random.uniform(10, 100), 2)
            results.append({
                "title": f"{keyword.capitalize()} Prodotto {i+1}",
                "url": f"https://www.amazon.{self.country}/dp/FAKEASIN{i+1}",
                "image": "https://via.placeholder.com/200x200.png?text=Prodotto+Fake",
                "price": f"{price}€",
                "discount": f"-{discount}%",
            })

        logging.info(f"📦 [MOCK] Risultati trovati per '{keyword}': {len(results)}")
        return results
