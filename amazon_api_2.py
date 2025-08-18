import logging
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.search_items_request import SearchItemsRequest
from paapi5_python_sdk.models.search_items_resource import SearchItemsResource
from paapi5_python_sdk.rest import ApiException
import time

def search_amazon(keyword, config):
    try:
        logging.info(f"Cercando prodotti per: {keyword}")

        default_api = DefaultApi(
            access_key=config['AMAZON_ACCESS_KEY'],
            secret_key=config['AMAZON_SECRET_KEY'],
            host='webservices.amazon.it',
            region='eu-west-1'
        )

        search_items_request = SearchItemsRequest(
            keywords=keyword,
            partner_tag=config['AMAZON_ASSOCIATE_TAG'],
            partner_type='Associates',
            marketplace='www.amazon.it',
            item_count=config['ITEM_COUNT'],
            resources=[
                SearchItemsResource.ITEMINFO_TITLE,
                SearchItemsResource.OFFERS_LISTINGS_PRICE,
                SearchItemsResource.ITEMINFO_FEATURES
            ]
        )

        response = default_api.search_items(search_items_request)
        logging.info(f"Trovati {len(response.search_result.items)} prodotti per la keyword: {keyword}")

        products_list = []
        for item in response.search_result.items:
            product = {
                'asin': item.asin,
                'url': item.detail_page_url,
                'title': None,
                'price': None,
                'discount': None
            }

            # Estrazione del titolo
            if item.item_info and item.item_info.title and item.item_info.title.display_value:
                product['title'] = item.item_info.title.display_value

            # Estrazione del prezzo e dello sconto
            if item.offers and item.offers.listings:
                listing = item.offers.listings[0]
                if listing.price and listing.price.amount:
                    product['price'] = listing.price.amount
                if listing.savings and listing.savings.percentage:
                    product['discount'] = listing.savings.percentage

            if product['title'] and product['url'] and product['price']:
                # Controlla se il prodotto ha uno sconto sufficiente
                if product['discount'] and product['discount'] >= config['MIN_SAVE']:
                    products_list.append(product)
                else:
                    logging.warning(f"Skipping product per sconto non sufficiente: {product['title']} (sconto {product['discount']})")
            else:
                logging.warning("Skipping product per attributi mancanti (title, url o price).")

        return products_list

    except ApiException as e:
        logging.error(f"Errore API Amazon: {e}")
        return []
    except Exception as e:
        logging.error(f"Errore sconosciuto: {e}")
        return []
