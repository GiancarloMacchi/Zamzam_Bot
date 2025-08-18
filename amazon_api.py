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
                # Check if price and other necessary attributes exist
                if hasattr(p, 'price') and hasattr(p.price, 'amount') and hasattr(p, 'detail_page_url') and hasattr(p, 'image_url'):
                    price_amount = p.price.amount
                    list_price_amount = None
                    discount_percentage = 0
                    
                    if hasattr(p, 'list_price') and hasattr(p.list_price, 'amount'):
                        list_price_amount = p.list_price.amount
                        if list_price_amount > 0:
                            discount_percentage = ((list_price_amount - price_amount) / list_price_amount) * 100
                    
                    # Apply the discount threshold
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
