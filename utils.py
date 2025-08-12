# utils.py
import os
import logging
import math
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from bitlyshortener import Shortener

logger = logging.getLogger(__name__)


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="***%(asctime)s - %(levelname)s - %(message)s"
    )


def get_config():
    # legge direttamente dalle env del runner / GitHub Secrets
    cfg = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "MIN_DISCOUNT": os.getenv("MIN_DISCOUNT"),  # percentuale, es 20
        "KEYWORDS": os.getenv("KEYWORDS", ""),
        "AMAZON_COUNTRY": os.getenv("AMAZON_COUNTRY", "it"),
        "BITLY_TOKEN": os.getenv("BITLY_TOKEN"),
    }
    return cfg


def check_required_config(cfg):
    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing = [k for k in required if not cfg.get(k)]
    return missing


# Semplice funzione per accorciare URL (opzionale)
def shorten_url(url, bitly_token=None):
    if not bitly_token:
        return url
    try:
        shortener = Shortener(tokens=[bitly_token], max_cache_size=256)
        res = shortener.shorten_urls([url])
        return res[0] if res and len(res) > 0 else url
    except Exception as e:
        logger.warning("Bitly shortener failed: %s", e)
        return url


# decide se il prodotto passa i filtri (sconto minimo e categorie italiane)
def qualifies_for_posting(product, cfg):
    """
    product: dict con keys almeno: title, price, original_price, discount_pct, url, category_hint
    cfg: config dict
    """
    min_disc = cfg.get("MIN_DISCOUNT")
    try:
        min_disc_val = int(min_disc) if min_disc else 20
    except Exception:
        min_disc_val = 20

    # sconto
    discount = product.get("discount_pct")
    if discount is None:
        logger.info("Scartato: nessun sconto calcolato per %s", product.get("title"))
        return False
    try:
        discount_val = float(discount)
    except Exception:
        discount_val = 0.0

    if discount_val < min_disc_val:
        logger.info("Scartato per sconto: %s - %.2f%% < %d%%", product.get("title"), discount_val, min_disc_val)
        return False

    # categoria hint (se presente) — controlliamo parole chiave italiane
    category_ok = False
    hint = (product.get("category_hint") or "").lower()
    keywords_cat = ["bambino", "bambini", "bimba", "bimbo", "infanzia", "mamma", "mamme", "genitori", "scuola", "gioco", "giocattolo", "libro", "videogioco", "giochi"]
    for k in keywords_cat:
        if k in hint:
            category_ok = True
            break

    # anche titolo può contenere parole chiave
    if not category_ok:
        title = (product.get("title") or "").lower()
        for k in keywords_cat:
            if k in title:
                category_ok = True
                break

    if not category_ok:
        logger.info("Scartato per categoria: %s (hint='%s')", product.get("title"), hint)
        return False

    return True


def make_message_for_product(product, cfg):
    title = product.get("title", "Prodotto")
    price = product.get("price")
    original = product.get("original_price")
    discount = product.get("discount_pct")
    url = product.get("url")
    if cfg.get("BITLY_TOKEN"):
        url = shorten_url(url, cfg.get("BITLY_TOKEN"))

    lines = []
    if price:
        lines.append(f"{title} - {price} - {url}")
    else:
        lines.append(f"{title} - {url}")
    if original:
        lines.append(f"Prezzo originale: {original}")
    if discount is not None:
        lines.append(f"Sconto: {discount}%")
    return "\n".join(lines)


def send_telegram_message(bot_token, chat_id, text):
    # invio semplice via API HTTP per ridurre dipendenze
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )
        resp.raise_for_status()
        logger.info("Messaggio inviato: %s", text[:80])
    except Exception as e:
        logger.error("Errore invio Telegram: %s", e)
