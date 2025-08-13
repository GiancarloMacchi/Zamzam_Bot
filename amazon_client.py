import os
import logging
from typing import List, Dict, Any, Iterable
from dotenv import load_dotenv

# ATTENZIONE: questo importa la LIBRERIA esterna "python-amazon-paapi".
# Assicurati di NON avere un file locale chiamato "amazon_paapi.py".
from amazon_paapi import AmazonApi

logger = logging.getLogger(__name__)
load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY", "")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY", "")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", "5") or "5")
MIN_SAVE = int(os.getenv("MIN_SAVE", "0") or "0")

# Inizializza client PA-API v5 (libreria di sergioteula)
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)


def _iter_results(results: Any) -> Iterable[Any]:
    """Supporta sia results.items sia results iterabile, per compatibilità."""
    if results is None:
        return []
    if hasattr(results, "items") and isinstance(results.items, Iterable):
        return results.items
    if isinstance(results, Iterable):
        return results
    return []


def _get_first(*vals):
    for v in vals:
        if v is not None:
            return v
    return None


def _safe_get_item_fields(item: Any) -> Dict[str, Any]:
    """Estrae campi in modo resiliente a differenze di modello tra wrapper."""
    # Titolo
    title = _get_first(
        getattr(item, "title", None),
        getattr(getattr(getattr(item, "item_info", None), "title", None), "display_value", None),
    )

    # URL dettaglio
    link = _get_first(
        getattr(item, "detail_page_url", None),
        getattr(item, "detailpageurl", None),
    )

    # Immagini (best effort)
    image_url = None
    images = getattr(item, "images", None)
    if images:
        image_url = _get_first(
            getattr(images, "large", None),
            getattr(images, "medium", None),
            getattr(images, "small", None),
        )
    if image_url is None:
        # Alcuni wrapper espongono image_sets
        image_sets = getattr(item, "image_sets", None)
        if image_sets and isinstance(image_sets, list) and image_sets:
            image_url = getattr(image_sets[0], "large", None) or getattr(image_sets[0], "medium", None)

    # Prezzi (lista/offerta)
    list_price = None
    offer_price = None
    # v5 tipica
    offers = getattr(item, "offers", None)
    if offers and getattr(offers, "listings", None):
        listing0 = offers.listings[0]
        price_obj = getattr(listing0, "price", None)
        if price_obj:
            offer_price = getattr(price_obj, "amount", None)
            currency = getattr(price_obj, "currency", None)
        # saving_basis → list_price
        saving_basis = getattr(listing0, "saving_basis", None)
        if saving_basis and getattr(saving_basis, "price", None):
            list_price = getattr(saving_basis.price, "amount", None)
    # wrapper "sergioteula" (alcune versioni)
    list_price = _get_first(list_price, getattr(getattr(item, "list_price", None), "amount", None))
    offer_price = _get_first(offer_price, getattr(getattr(item, "offer_price", None), "amount", None))
    currency = _get_first(
        locals().get("currency", None),
        getattr(getattr(item, "offer_price", None), "currency", None),
        getattr(getattr(item, "list_price", None), "currency", None),
    )

    # Calcolo sconto %
    discount = 0
    try:
        if list_price and offer_price and float(list_price) > 0:
            discount = int(((float(list_price) - float(offer_price)) / float(list_price)) * 100)
    except Exception:
        discount = 0

    return {
        "title": title or "Senza titolo",
        "link": link or "",
        "image_url": image_url,
        "list_price": list_price,
        "offer_price": offer_price,
        "currency": currency,
        "discount": discount,
    }


def get_items(keywords: str) -> List[Dict[str, Any]]:
    """
    Esegue una ricerca su Amazon per ogni keyword fornita e ritorna
    una lista normalizzata di item (titolo/link/immagine/prezzi/sconto).
    """
    if not keywords:
        logger.warning("Nessuna keyword fornita a get_items().")
        return []

    found: List[Dict[str, Any]] = []
    # Supporta lista di keyword separate da virgola
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    for kw in keyword_list:
        try:
            logger.info(f"🔍 Chiamata Amazon API con keyword: {kw}")
            # La libreria "sergioteula" accetta tipicamente (keywords, item_count)
            results = amazon.search_items(keywords=kw, item_count=ITEM_COUNT)

            for raw in _iter_results(results):
                item = _safe_get_item_fields(raw)
                if item["discount"] >= MIN_SAVE:
                    found.append(item)
        except Exception as e:
            logger.error("❌ Errore durante il recupero degli articoli da Amazon API:\n%s", e)

    return found
