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
                # Usa una logica più robusta per gestire i prezzi mancanti
                price_amount = p.price.amount if hasattr(p, 'price') and hasattr(p.price, 'amount') else None
                list_price_amount = p.list_price.amount if hasattr(p, 'list_price') and hasattr(p.list_price, 'amount') else None

                # Calcola lo sconto solo se entrambi i prezzi esistono
                if price_amount is not None and list_price_amount is not None and list_price_amount > 0:
                    discount_percentage = ((list_price_amount - price_amount) / list_price_amount) * 100
                else:
                    # Se non c'è il prezzo di listino, lo sconto è 0%
                    discount_percentage = 0
                
                # Applica la soglia di sconto
                if discount_percentage >= int(config['MIN_SAVE']):
                    results.append({
                        "title": p.title,
                        "url": p.detail_page_url,
                        "price": price_amount,
                        "original_price": list_price_amount,
                        "image": p.image_url,
                        "discount": int(discount_percentage)
                    })
        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
