# amazon_api.py
import os
import logging

logger = logging.getLogger(__name__)

try:
    from amazon_paapi import AmazonApi
except Exception:
    # se il package non è disponibile verrà lanciato errore in fase di esecuzione
    AmazonApi = None

AMAZON_REGION = "IT"


def get_amazon_client():
    """
    Crea e ritorna l'istanza AmazonApi.
    """
    if AmazonApi is None:
        raise RuntimeError("amazon_paapi package non disponibile. Controlla requirements.")
    access = os.getenv("AMAZON_ACCESS_KEY")
    secret = os.getenv("AMAZON_SECRET_KEY")
    tag = os.getenv("AMAZON_ASSOCIATE_TAG")

    if not (access and secret and tag):
        raise RuntimeError("Variabili Amazon mancanti: AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG")

    # La libreria python-amazon-paapi spesso prende (access_key, secret_key, partner_tag, marketplace)
    return AmazonApi(access, secret, tag, AMAZON_REGION)


def search_amazon_products(keyword, **kwargs):
    """
    Cerca prodotti su Amazon usando il client PAAPI.
    Ritorna una lista (anche vuota) di item (dictionary-like o oggetti).
    kwargs passati alla libreria (item_page, search_index, etc).
    """
    client = get_amazon_client()
    # la libreria usa .search_items(keywords=..., ...) => adattiamo
    # fallback generale: proviamo a chiamare search_items
    try:
        result = client.search_items(keywords=keyword, **kwargs)
    except TypeError:
        # se la firma è diversa
        result = client.search_items(keyword, **kwargs)

    # risultato può essere oggetto SearchResult con .items o dict con Items
    if result is None:
        return []

    # Se ha attributo items
    if hasattr(result, "items"):
        items = getattr(result, "items") or []
        return list(items)

    # Se è dict
    if isinstance(result, dict):
        items = result.get("Items") or result.get("items") or []
        return list(items)

    # Se è già un iterabile (list/tuple)
    if isinstance(result, (list, tuple)):
        return list(result)

    # Non riconosciuto -> ritorniamo singleton
    return [result]
    
