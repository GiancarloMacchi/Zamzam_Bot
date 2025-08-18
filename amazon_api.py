import logging
from amazon_paapi import AmazonApi

def search_amazon(keyword, config):
    try:
        client = AmazonApi(
            key=config['AMAZON_ACCESS_KEY'],
            secret=config['AMAZON_SECRET_KEY'],
            tag=config['AMAZON_ASSOCIATE_TAG'],
            country=config['AMAZON_COUNTRY']
        )
        search_results = client.search_items(
            keywords=keyword,
            item_count=int(config['ITEM_COUNT'])
        )
        products = search_results.items
        
        # Aggiungi questa riga per il debug
        logging.info(f"Trovati {len(products) if products else 0} prodotti per la keyword: {keyword}")

        results = []
        if products:
            for p in products:
                # Controlla se esistono sia il prezzo corrente che il prezzo di listino
                if hasattr(p, 'price') and hasattr(p.price, 'amount') and hasattr(p, 'list_price') and hasattr(p.list_price, 'amount'):
                    # Assicurati che il prezzo di listino sia maggiore di zero per evitare divisioni per zero
                    if p.list_price.amount > 0:
                        discount_percentage = ((p.list_price.amount - p.price.amount) / p.list_price.amount) * 100
                        if discount_percentage >= int(config['MIN_SAVE']):
                            results.append({
                                "title": p.title,
                                "url": p.detail_page_url,
                                "price": p.price.amount,
                                "original_price": p.list_price.amount,
                                "image": p.image_url,
                                "discount": int(discount_percentage)
                            })
        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
