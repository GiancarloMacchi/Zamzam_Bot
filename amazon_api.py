# amazon_api.py
import random

def get_amazon_products(keyword, max_results=5):
    """
    Restituisce una lista simulata di prodotti Amazon.
    In produzione, qui andrebbe l'integrazione con Amazon Product Advertising API.
    """
    prodotti = []
    for i in range(max_results):
        prodotti.append({
            "title": f"{keyword} prodotto {i+1}",
            "url": f"https://www.amazon.it/dp/B0{random.randint(10000000, 99999999)}",
            "price": f"{random.randint(10, 200)}.99 €"
        })
    return prodotti
