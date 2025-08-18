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
                if not hasattr(p, 'title') or not hasattr(p, 'detail_page_url') or not hasattr(p, 'price') or not hasattr(p.price, 'amount'):
                    logging.warning("Skipping product due to missing required attributes (title, url, or price).")
                    continue
                
                title = p.title.display_value
                url = p.detail_page_url
                price_amount = p.price.amount
                
                list_price_amount = None
                discount_percentage = 0
                
                # Se esiste, calcola lo sconto in base al prezzo di listino
                if hasattr(p, 'list_price') and hasattr(p.list_price, 'amount') and p.list_price.amount > 0:
                    list_price_amount = p.list_price.amount
                    discount_percentage = ((list_price_amount - price_amount) / list_price_amount) * 100
                
                logging.info(f"Prodotto '{title}' - Prezzo: {price_amount}, Prezzo di Listino: {list_price_amount}, Sconto Calcolato: {discount_percentage}%")
                
                # Condizione di pubblicazione:
                # 1. Pubblica se lo sconto è >= MIN_SAVE.
                # 2. Pubblica anche se non c'è prezzo di listino (perché non ha sconto).
                
                if discount_percentage >= int(config['MIN_SAVE']) or list_price_amount is None:
                    # Controlla che esista anche l'immagine, altrimenti il post Telegram non funzionerà
                    image_url = p.images.primary.large.url if hasattr(p, 'images') and hasattr(p.images, 'primary') and hasattr(p.images.primary, 'large') and hasattr(p.images.primary.large, 'url') else None
                    
                    if image_url:
                        results.append({
                            "title": title,
                            "url": url,
                            "price": price_amount,
                            "original_price": list_price_amount,
                            "image": image_url,
                            "discount": int(discount_percentage)
                        })

        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
