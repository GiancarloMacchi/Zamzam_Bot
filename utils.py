# utils.py
import os
import logging
import requests
from dotenv import load_dotenv
from decimal import Decimal

# carico .env se presente
load_dotenv()

logger = logging.getLogger(__name__)


def get_config():
    cfg = {
        "AMAZON_ACCESS_KEY": os.getenv("AMAZON_ACCESS_KEY"),
        "AMAZON_SECRET_KEY": os.getenv("AMAZON_SECRET_KEY"),
        "AMAZON_ASSOCIATE_TAG": os.getenv("AMAZON_ASSOCIATE_TAG"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "KEYWORDS": os.getenv("KEYWORDS"),  # CSV
        "BITLY_TOKEN": os.getenv("BITLY_TOKEN"),
        "MIN_DISCOUNT_PERCENT": os.getenv("MIN_DISCOUNT_PERCENT", "20"),
    }
    # normalizzo percent come int
    try:
        cfg["MIN_DISCOUNT_PERCENT"] = int(cfg["MIN_DISCOUNT_PERCENT"])
    except Exception:
        cfg["MIN_DISCOUNT_PERCENT"] = 20
    return cfg


def check_required_config(cfg):
    required = [
        "AMAZON_ACCESS_KEY",
        "AMAZON_SECRET_KEY",
        "AMAZON_ASSOCIATE_TAG",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    ]
    missing = [k for k in required if not cfg.get(k)]
    return missing


def _get_field(obj, *names):
    """
    Prova a leggere campi in modo robusto sia se obj è dict sia se è oggetto.
    Restituisce None se non disponibile.
    """
    for n in names:
        # dict-style nested using dot
        if isinstance(obj, dict):
            # supporta 'Offers.Listings.0.Price.Amount' (poco robusto),
            # proviamo a camminare
            try:
                parts = n.split(".")
                cur = obj
                ok = True
                for p in parts:
                    # if index like 0
                    if isinstance(cur, list):
                        try:
                            idx = int(p)
                            cur = cur[idx]
                        except Exception:
                            ok = False
                            break
                    elif isinstance(cur, dict):
                        cur = cur.get(p)
                    else:
                        ok = False
                        break
                if ok and cur is not None:
                    return cur
            except Exception:
                pass
        else:
            # try attribute
            try:
                cur = obj
                parts = n.split(".")
                ok = True
                for p in parts:
                    # numeric index
                    if hasattr(cur, "__iter__") and isinstance(cur, (list, tuple)) and p.isdigit():
                        cur = cur[int(p)]
                    else:
                        cur = getattr(cur, p)
                    if cur is None:
                        ok = False
                        break
                if ok and cur is not None:
                    return cur
            except Exception:
                pass
    return None


def _to_decimal(v):
    try:
        return Decimal(str(v))
    except Exception:
        return None


def qualifies_for_posting(product, cfg):
    """
    Controlla se il prodotto deve essere pubblicato:
    - deve avere Offers
    - sconto >= MIN_DISCOUNT_PERCENT (se calcolabile)
    - titolo o categorie contengono parole italiane di categoria (baby, bambino, mamma, scuola, giocattolo, libro...)
    Se non è possibile calcolare lo sconto in modo affidabile, il prodotto viene scartato.
    """
    MIN_PCT = cfg.get("MIN_DISCOUNT_PERCENT", 20)

    # 1) verifica Offers
    offers = _get_field(product, "offers", "Offers", "Offers.Listings", "offers.listings")
    if not offers:
        logger.info("🔵 Nessuna offerta per '%s', salto...", _get_field(product, "title", "item_info.title.display_value", "ItemInfo.Title.DisplayValue") or "")
        return False

    # Cerca prezzo corrente
    price = _get_field(product,
                       "offers.Listings.0.Price.Amount",
                       "offers.listings.0.price.amount",
                       "Offers.Listings.0.Price.Amount",
                       "Offers.Listings.0.Price.DisplayAmount",
                       "price",
                       "ItemInfo.ByLineInfo")
    # Cerca prezzo listino (prezzo originale)
    list_price = _get_field(product,
                            "offers.Listings.0.Price.ListPrice.Amount",
                            "offers.listings.0.price.listPrice.amount",
                            "Offers.Listings.0.Price.ListPrice.Amount",
                            "ItemInfo.ListPrice.Price.Amount",
                            "list_price")

    # Estrazioni alternative
    # Alcune strutture usano 'price.amount' e 'price.savings' o 'saving_amount'
    if price is None:
        price = _get_field(product, "buybox_price", "Offers.Listings.0.Price.Amount")

    if list_price is None:
        # prova a prendere "ItemInfo.ListPrice"
        list_price = _get_field(product, "ItemInfo.ListPrice.DisplayAmount", "ItemInfo.ListPrice.Price")

    # Se non abbiamo entrambi, non possiamo calcolare sconto in modo affidabile -> salto
    if price is None or list_price is None:
        logger.info("🔵 Sconto non calcolabile (mancano prezzi) per '%s', salto...", _get_field(product, "title", "item_info.title.display_value") or "")
        return False

    # converti a numerico se possibile (rimuovi simboli)
    def extract_number(x):
        if x is None:
            return None
        # se è dict con Amount
        if isinstance(x, dict) and x.get("Amount") is not None:
            return _to_decimal(x.get("Amount"))
        # se è oggetto con amount attr
        try:
            if hasattr(x, "amount"):
                return _to_decimal(getattr(x, "amount"))
        except Exception:
            pass
        # se è stringa tipo '€ 12,34'
        if isinstance(x, str):
            s = x.replace("€", "").replace(",", ".").replace(" ", "").strip()
            # tolgo altri simboli
            filtered = "".join(ch for ch in s if (ch.isdigit() or ch == "."))
            try:
                return _to_decimal(filtered)
            except Exception:
                return None
        # se è già numerico
        try:
            return _to_decimal(x)
        except Exception:
            return None

    p = extract_number(price)
    lp = extract_number(list_price)

    if p is None or lp is None or lp == 0:
        logger.info("🔵 Prezzi non interpretabili per '%s', salto...", _get_field(product, "title", "item_info.title.display_value") or "")
        return False

    try:
        discount_pct = (lp - p) / lp * 100
    except Exception:
        return False

    if discount_pct < MIN_PCT:
        logger.info("🔵 Sconto %0.1f%% inferiore al minimo per '%s', salto...", float(discount_pct), _get_field(product, "title", "item_info.title.display_value") or "")
        return False

    # 3) filtro categoria/lingua (semplice keyword match titolo)
    title = _get_field(product, "title", "item_info.title.display_value", "ItemInfo.Title.DisplayValue")
    if title:
        title_low = str(title).lower()
        allowed_keywords = ["bambino", "bambini", "neonato", "mamma", "bambina", "infanzia", "scuola", "libro", "gioco", "giocattolo", "kids", "children"]
        if not any(k in title_low for k in allowed_keywords):
            logger.info("🔵 Titolo non in categorie target per '%s', salto...", title)
            return False
    else:
        logger.info("🔵 Titolo mancante, salto...")
        return False

    # se tutto ok
    return True


def make_affiliate_link(product, cfg):
    """
    Ritorna un link amazon con associate tag se possibile.
    Cerca un URL nel prodotto altrimenti costruisce via ASIN.
    """
    # prova a leggere URL diretto
    url = _get_field(product, "detail_page_url", "DetailPageURL", "item_info.urls.detail_page_url", "Offers.Listings.0.DetailPageURL")
    if not url:
        # prova ASIN
        asin = _get_field(product, "asin", "ASIN", "ItemInfo.ByLineInfo")
        if asin:
            url = f"https://www.amazon.it/dp/{asin}"
    if not url:
        return None

    tag = cfg.get("AMAZON_ASSOCIATE_TAG")
    if tag:
        # se già contiene tag, non lo aggiungiamo due volte
        if "tag=" in url or "linkCode=" in url:
            return url
        # aggiungiamo ?tag=... o &tag=...
        sep = "&" if ("?" in url) else "?"
        return f"{url}{sep}tag={tag}"
    return url


def shorten_link(url, cfg):
    """
    Se BITLY_TOKEN presente usa Bitly API v4 via requests per accorciare.
    Altrimenti ritorna l'URL originale.
    """
    token = cfg.get("BITLY_TOKEN")
    if not token or not url:
        return url
    try:
        resp = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            json={"long_url": url},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            return data.get("link") or url
        logger.warning("Bitly error %s: %s", resp.status_code, resp.text)
        return url
    except Exception as e:
        logger.exception("Errore Bitly: %s", e)
        return url


def make_message_for_product(product, cfg):
    title = _get_field(product, "title", "item_info.title.display_value", "ItemInfo.Title.DisplayValue") or "Prodotto Amazon"
    # trova prezzo corrente
    price = _get_field(product, "offers.Listings.0.Price.Amount", "offers.listings.0.price.amount", "price", "Price.Amount")
    list_price = _get_field(product, "offers.Listings.0.Price.ListPrice.Amount", "offers.listings.0.price.listPrice.amount", "list_price", "ItemInfo.ListPrice.Price")

    # formato prezzi
    def fmt(x):
        if x is None:
            return "N/D"
        if isinstance(x, dict):
            v = x.get("Amount") or x.get("amount") or x.get("value")
            if v is None:
                return str(x)
            return f"€{v}"
        return str(x)

    url = make_affiliate_link(product, cfg)
    short = shorten_link(url, cfg)

    # calcola percentuale se possibile
    p_num = None
    lp_num = None
    try:
        from decimal import Decimal
        # estrai numerico dalla stringa
        def to_num(x):
            if x is None:
                return None
            if isinstance(x, dict):
                a = x.get("Amount") or x.get("amount")
                return Decimal(str(a)) if a is not None else None
            if isinstance(x, (int, float, Decimal)):
                return Decimal(str(x))
            s = str(x).replace("€", "").replace(",", ".").strip()
            s = "".join(ch for ch in s if (ch.isdigit() or ch == "."))
            return Decimal(s) if s else None

        p_num = to_num(price)
        lp_num = to_num(list_price)
        pct = None
        if p_num and lp_num and lp_num > 0:
            pct = (lp_num - p_num) / lp_num * 100
    except Exception:
        pct = None

    parts = []
    parts.append(f"{title}")
    if price:
        parts.append(f"Prezzo: {fmt(price)}")
    if list_price:
        parts.append(f"Listino: {fmt(list_price)}")
    if pct is not None:
        parts.append(f"Sconto: {float(pct):0.1f}%")
    if short:
        parts.append(short)
    message = " - ".join(parts)
    return message


def send_telegram_message(bot_token, chat_id, text):
    """
    Invio tramite Telegram Bot API con requests (no dipendenza aggiuntiva).
    """
    if not bot_token or not chat_id:
        logger.error("Telegram token o chat_id mancanti, non invio.")
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        if resp.status_code in (200, 201):
            return True
        logger.error("Telegram API errore %s: %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logger.exception("Errore invio Telegram: %s", e)
        return False
