import logging
import os
from amazon_paapi.api import AmazonApi
import time

def search_amazon(keyword, config):
    try:
        logging.info(f"Cercando prodotti per: {keyword}")

        amazon = AmazonApi(
            key=config['AMAZON_ACCESS_KEY'],
            secret=config['AMAZON_SECRET_KEY'],
            tag=config['AMAZON_ASSOCIATE_TAG'],
            country=config['AMAZON_COUNTRY']
        )
        
        products_response = amazon.search_items(keywords=keyword)
        
        items_list = products_response.items
        
        logging.info(f"Trovati {len(items_list)} prodotti per la keyword: {keyword}")

        products_list = []
        for p in items_list:
            product = {
                'title': p.item_info.title.display_value if p.item_info and p.item_info.title else None,
                'url': p.detail_page_url,
                'price': None,
                'discount': None
            }
            
            # Controllo se esistono offerte per il prodotto
            if p.offers and p.offers.listings:
                listing = p.offers.listings[0]
                if listing.price and listing.price.amount:
                    product['price'] = listing.price.amount
                if listing.price and listing.price.savings and listing.price.savings.percentage:
                    product['discount'] = listing.price.savings.percentage

            if product['title'] and product['url'] and product['price']:
                # Controlla se il prodotto ha uno sconto sufficiente
                if product['discount'] and product['discount'] >= config['MIN_SAVE']:
                    products_list.append(product)
                else:
                    logging.warning(f"Skipping product per sconto non sufficiente: {product['title']} (sconto {product['discount']})")
            else:
                logging.warning("Skipping product per attributi mancanti (title, url o price).")

        return products_list

    except Exception as e:
        logging.error(f"Errore durante la ricerca Amazon: {e}")
        return []
