# utils.py
import os
import logging
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, urljoin

from amazon_api import search_amazon

logger = logging.getLogger(__name__)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="***%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger("zamzam")

def get_config():
    # legge .env se presente tramite python-dotenv (optional)
    from dotenv import load_dotenv
    load_dotenv()
    cfg = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "AMAZON_ASSOCIATE_TAG": os.getenv("AMAZON_ASSOCIATE_TAG"),
        "KEYWORDS": os.getenv("KEYWORDS"),
        "MIN_DISCOUNT": float(os.getenv("MIN_DISCOUNT") or 20.0),
        "AMAZON_COUNTRY": os.getenv("AMAZON_COUNTRY") or "it",
    }
    return cfg

def check_required_config(cfg):
    missing = []
    if not cfg.get("TELEGRAM_BOT_TOKEN"):
        missing.append("TELEGRAM_BOT_TOKEN")
    if not cfg.get("TELEGRAM_CHAT_ID"):
        missing.append("TELEGRAM_CHAT_ID")
    return missing

def search_amazon_products(cfg, keyword):
    # wrapper: restituisce lista di products (come dict) o []
    return search_amazon(keyword, country_code=cfg.get("AMAZON_COUNTRY", "it"))

def is_relevant_category(title):
    """
    Controllo semplice se il titolo contiene parole italiane inerenti a bambini/infanzia/scuola/giocattoli.
    """
    if not title:
        return False
    title_lower = title.lower()
    keywords = [
        "bambino", "bambini", "neonato", "neonati", "neonata", "mamma", "mamme",
        "infanzia", "gioco", "giocattolo", "giochi", "bimbo", "scuola", "cartoleria",
        "libro", "libri", "ragazzo", "ragazza", "teen", "peluche", "puzzle", "lego", "videogioco"
    ]
    return any(k in title_lower for k in keywords)

def qualifies_for_posting(product, cfg):
    """
    Decide se il prodotto va pubblicato:
    - deve avere 'has_offer' True o discount >= MIN_DISCOUNT
    - titolo deve appartenere alle categorie rilevanti (italiano)
    """
    try:
        title = product.get("title") or ""
        if not is_relevant_category(title):
            logger.info("Sconto scartato per categoria non rilevante per '%s', salto...", title)
            return False

        discount = product.get("discount")
        min_disc = float(cfg.get("MIN_DISCOUNT", 20.0))
        has_offer = product.get("has_offer", False)

        if has_offer and discount is not None:
            if discount >= min_disc:
                return True
            else:
                logger.info("Sconto %s%% inferiore al minimo per '%s', salto...", discount, title)
                return False
        # se non abbiamo discount ma abbiamo list_price e price, calcoliamo
        list_price = product.get("list_price")
        price = product.get("price")
        if price and list_price:
            try:
                disc = round((list_price - price) / list_price * 100, 1)
                if disc >= min_disc:
                    return True
                else:
                    logger.info("Sconto calcolato %s%% inferiore al minimo per '%s', salto...", disc, title)
                    return False
            except Exception:
                return False

        return False
    except Exception as e:
        logger.exception("Errore qualifies_for_posting: %s", e)
        return False

def append_affiliate_tag(url, tag):
    """
    Appende query param tag=AMAZON_ASSOCIATE_TAG al link Amazon se possibile.
    Se url è None prova ad usare asin.
    """
    if not url:
        return None
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs["tag"] = [tag]
        new_q = urlencode({k: v[0] for k, v in qs.items()})
        new = parsed._replace(query=new_q)
        return urlunparse(new)
    except Exception:
        # fallback: append simple
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}tag={tag}"

def make_message_for_product(product, cfg):
    title = product.get("title") or "Prodotto"
    price = product.get("price")
    list_price = product.get("list_price")
    discount = product.get("discount")
    url = product.get("url")
    asin = product.get("asin")
    if not url and asin:
        url = f"https://www.amazon.{cfg.get('AMAZON_COUNTRY','it')}/dp/{asin}"

    tag = cfg.get("AMAZON_ASSOCIATE_TAG")
    if tag:
        url = append_affiliate_tag(url, tag)

    parts = [f"{title}"]
    if price:
        parts.append(f"- {price:.2f} €")
    if list_price:
        parts.append(f"(listino {list_price:.2f} €)")
    if discount:
        parts.append(f"- Sconto {discount}%")
    if url:
        parts.append(f"- {url}")

    return " ".join(parts)

def send_telegram_message(bot_token, chat_id, text):
    if not bot_token or not chat_id or not text:
        logger.error("Parametri Telegram mancanti")
        return False
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": False,
            "parse_mode": "HTML"
        }
        r = requests.post(api_url, data=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.exception("Errore invio Telegram: %s", e)
        return False
