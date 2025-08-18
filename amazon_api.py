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
        
        logging.info(f"Trovati {len(products) if products else 0} prodotti per la keyword: {keyword}")

        results = []
        if products:
            for p in products:
                # Controlla se il prodotto ha almeno il prezzo di vendita e l'URL
                if hasattr(p, 'price') and hasattr(p.price, 'amount') and hasattr(p, 'detail_page_url'):
                    price_amount = p.price.amount
                    list_price_amount = None
                    discount_percentage = 0
                    
                    # Se esiste, calcola lo sconto in base al prezzo di listino
                    if hasattr(p, 'list_price') and hasattr(p.list_price, 'amount') and p.list_price.amount > 0:
                        list_price_amount = p.list_price.amount
                        discount_percentage = ((list_price_amount - price_amount) / list_price_amount) * 100
                    
                    # Aggiungi il prodotto se supera la soglia di sconto (anche se è 0)
                    if discount_percentage >= int(config['MIN_SAVE']):
                        # Controlla che esista anche l'immagine, altrimenti il post Telegram non funzionerà
                        image_url = p.image_url if hasattr(p, 'image_url') else None
                        
                        if image_url:
                            results.append({
                                "title": p.title,
                                "url": p.detail_page_url,
                                "price": price_amount,
                                "original_price": list_price_amount,
                                "image": image_url,
                                "discount": int(discount_percentage)
                            })
        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
