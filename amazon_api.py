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
        products = client.search_items(keywords=keyword, item_count=int(config['ITEM_COUNT']))
        results = []
        for p in products:
            if p.price_and_currency and p.original_price and p.original_price[0] > 0:
                discount_percentage = ((p.original_price[0] - p.price_and_currency[0]) / p.original_price[0]) * 100
                if discount_percentage >= int(config['MIN_SAVE']):
                    results.append({
                        "title": p.title,
                        "url": p.detail_page_url,
                        "price": p.price_and_currency[0],
                        "original_price": p.original_price[0],
                        "image": p.large_image_url,
                        "discount": int(discount_percentage)
                    })
        return results
    except Exception as e:
        logging.warning(f"Errore API Amazon: {e}")
        return []
