import logging
import json
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

        if not products:
            return []

        # DEBUG: stampa il primo prodotto grezzo in JSON
        try:
            raw = products[0].__dict__
            logging.debug("Primo prodotto grezzo:\n" + json.dumps(raw, indent=2, default=str))
        except Exception as e:
            logging.debug(f"Impossibile serializzare il primo prodotto: {e}")

        results = []
        for p in products:
            # Titolo fallback
            title = getattr(p, "title", None)
            if not title and hasattr(p, "item_info") and hasattr(p.item_info, "title"):
                title = getattr(p.item_info.title, "display_value", None)

            # URL
            url = getattr(p, "detail_page_url", None)

            # Prezzo fallback
            price_amount = None
            if hasattr(p, "price") and hasattr(p.price, "amount"):
                price_amount = p.price.amount
            elif hasattr(p, "offers") and hasattr(p.offers, "listings"):
                try:
                    price_amount = p.offers.listings[0].price.amount
                except Exception:
                    pass

            # Prezzo di listino (per calcolo sconto)
            list_price_amount = None
            if hasattr(p, "list_price") and hasattr(p.list_price, "amount"):
                list_price_amount = p.list_price.amount
            elif hasattr(p, "offers") and hasattr(p.offers, "listings"):
                try:
                    list_price_amount = p.offers.listings[0].price.savings_basis
                except Exception:
                    pass

            # Se mancano i campi essenziali, skip
            if not title or not url or not price_amount:
                logging.warning("Skipping product per attributi mancanti (title, url o price).")
                continue

            # Calcolo sconto
            discount_percentage = 0
            if list_price_amount and list_price_amount > 0:
                discount_percentage = ((list_price_amount - price_amount) / list_price_amount) * 100

            logging.info(f"Prodotto '{title}' - Prezzo: {price_amount}, Prezzo di Listino: {list_price_amount}, Sconto Calcolato: {discount_percentage}%")

            # **CORREZIONE**: Aggiungi la condizione per i prodotti senza sconto
            if discount_percentage >= int(config['MIN_SAVE']) or list_price_amount is None:
                image_url = getattr(p, "image_url", None)
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
