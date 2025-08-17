import logging
from amazon_paapi import AmazonAPI

def search_amazon(keywords, item_count=5):
    results = []
    for kw in keywords:
        logging.info(f"Cercando prodotti per: {kw}")
        # Inserisci qui la logica reale o di test
        # Simulazione DRY_RUN se configurato
        for i in range(1, item_count + 1):
            results.append({
                "title": f"{kw} Prodotto {i}",
                "url": f"https://www.amazon.***/dp/EXAMPLE{i}",
                "price": f"{i*10},99€",
                "image": f"https://via.placeholder.com/150?text={kw}+{i}",
                "description": f"Breve descrizione di {kw} {i}"
            })
    return results
