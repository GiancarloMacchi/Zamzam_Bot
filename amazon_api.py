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
                try:
                    title = p.title
                    url = p.detail_page_url
                    image_url = p.image_url
                    price_amount = p.price.amount
                    
                    list_price_amount = None
                    discount_percentage = 0
                    
                    # Try to get list price and calculate discount
                    if hasattr(p, 'list_price') and hasattr(p.list_price, 'amount') and p.list_price.amount > 0:
                        list_price_amount = p.list_price.amount
                        discount_percentage = ((list_price_amount - price_amount) / list_price_amount) * 100
                    
                    # Check if the discount is enough
                    if discount_percentage >= int(config['MIN_SAVE']):
                        results.append({
                            "title": title,
                            "url": url,
                            "price": price_amount,
                            "original_price": list_price_amount,
                            "image": image_url,
                            "discount": int(discount_percentage)
                        })
                except Exception as e:
                    # Log a warning if a product can't be processed
                    logging.warning(f"Skipping product due to missing attribute: {e}")
        
        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
