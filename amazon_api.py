# amazon_api.py
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote_plus, urljoin

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _search_url(keyword, country_code="it"):
    base = {
        "it": "https://www.amazon.it",
        "de": "https://www.amazon.de",
        "fr": "https://www.amazon.fr",
        "es": "https://www.amazon.es",
        "co.uk": "https://www.amazon.co.uk",
        "com": "https://www.amazon.com",
    }.get(country_code, "https://www.amazon.it")
    return f"{base}/s?k={quote_plus(keyword)}"


def _fetch_search_page(keyword, country_code="it"):
    url = _search_url(keyword, country_code)
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.text


def _parse_price(text):
    # tenta estrarre valore numerico in euro
    if not text:
        return None
    t = text.replace("\u00a0", " ").replace(",", ".")
    digits = "".join(ch for ch in t if ch.isdigit() or ch in ".")
    try:
        if digits:
            # se numeri multipli prendi ultimo
            parts = digits.split(".")
            if len(parts) >= 2:
                # ricomponi, ultimo due cifre sono centesimi? tentativo
                return t.strip()
            return t.strip()
    except Exception:
        pass
    return t.strip()


def search_amazon(keyword, country_code="it"):
    """
    Restituisce lista di prodotti: ogni prodotto dict con keys:
    title, price, original_price, discount_pct, url, asin, category_hint
    """
    try:
        html = _fetch_search_page(keyword, country_code)
    except Exception as e:
        logger.error("Errore fetch Amazon: %s", e)
        raise

    soup = BeautifulSoup(html, "html.parser")
    results = []
    # i blocchi tipici sono div con data-asin
    items = soup.find_all("div", {"data-asin": True})
    for it in items:
        asin = it.get("data-asin") or ""
        if not asin:
            continue
        # titolo
        title_tag = it.find("span", {"class": "a-size-medium"})
        if not title_tag:
            title_tag = it.find("span", {"class": "a-size-base-plus"})
        title = title_tag.get_text(strip=True) if title_tag else ""

        # url
        a = it.find("a", {"class": "a-link-normal", "href": True})
        url = urljoin("https://www.amazon.it", a["href"]) if a else ""

        # prezzo attuale
        price_tag = it.find("span", {"class": "a-offscreen"})
        price = _parse_price(price_tag.get_text()) if price_tag else None

        # prezzo precedente / crossed
        orig_tag = it.find("span", {"class": "a-price a-text-price"})
        original_price = None
        if orig_tag:
            sp = orig_tag.find("span", {"class": "a-offscreen"})
            original_price = _parse_price(sp.get_text()) if sp else None

        # tentativo di estrarre percentuale sconto visibile
        discount_pct = None
        disc_tag = it.find(text=lambda t: t and "%" in t)
        if disc_tag:
            txt = disc_tag.strip()
            # cerca percentuale
            import re
            m = re.search(r"(\d{1,2})\s*%", txt)
            if m:
                discount_pct = int(m.group(1))

        # se abbiamo prezzo e original possiamo calcolare percentuale
        if discount_pct is None and price and original_price:
            try:
                # rimuovi simboli e trasform in float quando possibile
                def num(s):
                    import re
                    s2 = re.sub(r"[^\d,\.]", "", s)
                    s2 = s2.replace(",", ".")
                    return float(s2)
                p = num(price)
                o = num(original_price)
                if o and o > p:
                    discount_pct = round((o - p) / o * 100, 2)
            except Exception:
                discount_pct = None

        results.append({
            "asin": asin,
            "title": title,
            "url": url,
            "price": price,
            "original_price": original_price,
            "discount_pct": discount_pct,
            "category_hint": "",  # non facile da estrarre in search page
        })

    return results


# API compat wrapper
def search_amazon_products(keyword, country_code="it"):
    return search_amazon(keyword, country_code)
