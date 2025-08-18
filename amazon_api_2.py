import logging
import os
from amazon_paapi import AmazonAPI
import time

def search_amazon(keyword, config):
    try:
        logging.info(f"Cercando prodotti per: {keyword}")

        amazon = AmazonAPI(
            access_key=config['AMAZON_ACCESS_KEY'],
            secret_key=config['AMAZON_SECRET_KEY'],
            associate_tag=config['AMAZON_ASSOCIATE_TAG'],
            country=config['AMAZON_COUNTRY']
        )
        
        products = amazon.search_items(keywords=keyword)
        
        logging.info(f"Trovati {len(products)} prodotti per la keyword: {keyword}")

        products_list = []
        for p in products:
            product = {
                'title': p.title,
                'url': p.url,
                'price': p.price,
                'discount': p.discount
            }

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
