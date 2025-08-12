# utils.py
import os
import logging
import re
import requests
from decimal import Decimal, InvalidOperation
import amazon_api  # usa il tuo amazon_api.py personalizzato

logger = logging.getLogger(__name__)


def get_config():
    """
    Legge le variabili d'ambiente e rimette in un dict uniforme.
    Nota: cerca prima AMAZON_ASSOCIATE_TAG poi PARTNER_TAG (fallback).
    """
    return {
        "AMAZON_ACCESS_KEY": os.getenv("AMAZON_ACCESS_KEY"),
        "AMAZON_SECRET_KEY": os.getenv("AMAZON_SECRET_KEY"),
        # supporta entrambe le varianti
        "AMAZON_ASSOCIATE_TAG": os.getenv("AMAZON_ASSOCIATE_TAG") or os.getenv("PARTNER_TAG"),
        "AMAZON_REGION": os.getenv("AMAZON_REGION") or "eu-west-1",
        "AMAZON_HOST": os.getenv("AMAZON_HOST") or "webservices.amazon.it",
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "KEYWORDS": os.getenv("KEYWORDS", ""),  # es. "baby,giochi,scuola"
        # filtri configurabili
        "MIN_DISCOUNT_PERCENT": Decimal(os.getenv("MIN_DISCOUNT_PERCENT", "20")),
        "CATEGORY_TERMS": [t.strip().lower() for t in (os.getenv("CATEGORY_TERMS", "bambino,bambini,mamma,neonato,gioco,giocattolo,scuola,libro,ragazzi")).split(",") if t.strip()],
    }


def check_required_config(cfg):
    required = {
        "AMAZON_ACCESS_KEY": cfg.get("AMAZON_ACCESS_KEY"),
        "AMAZON_SECRET_KEY": cfg.get("AMAZON_SECRET_KEY"),
        "AMAZON_ASSOCIATE_TAG": cfg.get("AMAZON_ASSOCIATE_TAG"),
        "TELEGRAM_BOT_TOKEN": cfg.get("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": cfg.get("TELEGRAM_CHAT_ID"),
    }
    missing = [k for k, v in required.items() if not v]
    return missing


def safe_decimal(val):
    if val is None:
        return None
    try:
        # rimuove ogni cosa non numerica tranne la virgola o il punto
        s = re.sub(r"[^\d,\.]", "", str(val))
        s = s.replace(",", ".")
        return Decimal(s) if s != "" else None
    except (InvalidOperation, ValueError):
        return None


def extract_title(item):
    # prova più percorsi possibili per trovare il titolo
    t = (
        item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue")
        or item.get("ItemInfo", {}).get("Title", {}).get("Label")
        or item.get("title")
        or item.get("Title")
        or ""
    )
    return str(t).strip()


def extract_prices(item):
    """
    Cerca di estrarre price e list_price in molti possibili formati di risposta.
    Restituisce (price_decimal, list_price_decimal) oppure (None, None)
    """
    # 1) struttura classica PA-API: Offers -> Listings -> Price -> Amount
    try:
        offers = item.get("Offers") or {}
        listings = offers.get("Listings") if isinstance(offers, dict) else None
        if listings and isinstance(listings, list) and len(listings) > 0:
            price_node = listings[0].get("Price") or {}
            amount = price_node.get("Amount") or price_node.get("DisplayAmount") or price_node.get("Value")
            # list price
            list_price_node = item.get("Offers", {}).get("Listings", [])[0].get("Price", {}).get("Savings") if False else None
            # Fall back
            list_price = None
            if item.get("ItemInfo", {}).get("ProductInfo", {}).get("ListPrice"):
                list_price = item["ItemInfo"]["ProductInfo"]["ListPrice"].get("Amount")
            return safe_decimal(amount), safe_decimal(list_price)
    except Exception:
        pass

    # 2) campi alternativi
    # some responses contain OfferSummary or Offers.Listings[0].Price or Offers.Listings[0].Price.Amount
    try:
        if item.get("Offers"):
            # try generic parse
            o = item["Offers"]
            # if Offers is a dict and has 'Listings'
            if isinstance(o, dict):
                l = o.get("Listings")
                if l and isinstance(l, list) and len(l) > 0:
                    amt = l[0].get("Price", {}).get("Amount") or l[0].get("Price", {}).get("Value")
                    lp = item.get("ItemInfo", {}).get("ProductInfo", {}).get("ListPrice", {}).get("Amount")
                    return safe_decimal(amt), safe_decimal(lp)
    except Exception:
        pass

    # 3) fallback su campi generici
    price = item.get("price") or item.get("Price") or None
    list_price = item.get("list_price") or item.get("ListPrice") or None
    return safe_decimal(price), safe_decimal(list_price)


def compute_discount_percent(price, list_price):
    try:
        if price is None or list_price is None:
            return None
        if list_price == 0:
            return None
        return ( (list_price - price) / list_price ) * 100
    except Exception:
        return None


def is_italian(item):
    """
    Semplice filtro: controlla se il titolo contiene parole italiane (heuristic).
    Potremmo migliorare con altri campi se disponibili.
    """
    title = extract_title(item).lower()
    # se il titolo ha almeno una parola italiana della lista considerala italiana
    italian_terms = ["edizione", "ediz.", "ediz", "rilegato", "cartonato", "bambino", "bambini", "mamma", "neonato"]
    return any(t in title for t in italian_terms)


def category_match(item, cfg):
    title = extract_title(item).lower()
    for term in cfg["CATEGORY_TERMS"]:
        if term in title:
            return True
    # se ci sono info categoria, possiamo espandere la match in futuro
    return False


def search_amazon_products(cfg, keywords):
    """
    Wrapper intorno ad amazon_api.get_amazon_products; restituisce la lista di items
    """
    # amazon_api.get_amazon_products(keywords, amazon_access_key, amazon_secret_key, amazon_tag, ...)
    data = amazon_api.get_amazon_products(
        keywords,
        cfg["AMAZON_ACCESS_KEY"],
        cfg["AMAZON_SECRET_KEY"],
        cfg["AMAZON_ASSOCIATE_TAG"],
        region=cfg["AMAZON_REGION"],
        host=cfg["AMAZON_HOST"],
    )
    # il modulo amazon_api.py dovrebbe restituire una struttura standard; gestiamo difetti
    # se ritorna dict con SearchResult.Items
    if isinstance(data, dict):
        # più possibili percorsi
        items = data.get("SearchResult", {}).get("Items") or data.get("items") or data.get("Items") or []
        return items
    # se è già una list
    if isinstance(data, (list, tuple)):
        return list(data)
    return []


def qualifies_for_posting(item, cfg):
    """
    Applica i filtri: deve avere offers, deve avere sconto >= MIN_DISCOUNT_PERCENT, deve appartenere a categoria
    """
    # Salta se non ha offerte
    offers = item.get("Offers") or item.get("offers") or {}
    if not offers:
        logger.info("⛔ Nessuna offerta per '%s', salto...", extract_title(item))
        return False

    price, list_price = extract_prices(item)
    if price is None or list_price is None:
        logger.info("ℹ️ Sconto 0% o prezzi non disponibili per '%s', salto...", extract_title(item))
        return False

    discount = compute_discount_percent(price, list_price)
    if discount is None:
        logger.info("ℹ️ Sconto non calcolabile per '%s', salto...", extract_title(item))
        return False

    if discount < cfg["MIN_DISCOUNT_PERCENT"]:
        logger.info("ℹ️ Sconto %s%% inferiore al minimo per '%s', salto...", str(discount.quantize(Decimal("0.1"))), extract_title(item))
        return False

    # filtro categoria
    if not category_match(item, cfg):
        logger.info("ℹ️ Categoria non corrisponde per '%s', salto...", extract_title(item))
        return False

    # lingua (heuristic)
    if not is_italian(item):
        logger.info("ℹ️ Probabilmente non italiano per '%s', salto...", extract_title(item))
        return False

    return True


def make_message_for_product(item, cfg):
    title = extract_title(item)
    price, list_price = extract_prices(item)
    # link con partner tag: cerco asin o detail page
    link = None
    # PAAPI often includes DetailPageURL
    link = item.get("DetailPageURL") or item.get("detailPageURL") or item.get("DetailPageUrl")
    # fallback: if ASIN is present, compongo url Amazon.it
    asin = item.get("ASIN") or item.get("asin") or item.get("ASINs")
    if not link and asin:
        link = f"https://www.amazon.it/dp/{asin}?tag={cfg['AMAZON_ASSOCIATE_TAG']}"

    # se link contiene già parametri, assicurati che tag ci sia:
    if link and "tag=" not in link and cfg["AMAZON_ASSOCIATE_TAG"]:
        sep = "&" if "?" in link else "?"
        link = f"{link}{sep}tag={cfg['AMAZON_ASSOCIATE_TAG']}"

    price_str = f"{price}€" if price else "Prezzo non disponibile"
    list_price_str = f"{list_price}€" if list_price else "N/D"

    msg = f"{title} - {price_str} - {link}"
    return msg


def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload, timeout=15)
    if not r.ok:
        logger.error("Errore invio Telegram: %s - %s", r.status_code, r.text)
        raise Exception(f"Telegram error {r.status_code}: {r.text}")
    logger.info("Invio completato ✅")
    return True
