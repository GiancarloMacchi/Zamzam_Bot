# amazon_api.py
import requests
from bs4 import BeautifulSoup
import logging
import time
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
}

def _fetch_search_page(keyword, country_code="it"):
    q = keyword.strip()
    url = f"https://www.amazon.{country_code}/s"
    params = {"k": q}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.text

def _parse_price(soup_price_whole, soup_price_frac):
    try:
        whole = soup_price_whole.get_text().strip().replace(".", "").replace(",", "")
        frac = soup_price_frac.get_text().strip() if soup_price_frac else "00"
        # whole might be like "12" and frac "99"
        # We will try to convert to float: join with comma decimal
        price_str = whole
        if frac:
            price_str = f"{whole}.{frac}"
        return float(price_str)
    except Exception:
        return None

def search_amazon(keyword, country_code="it", max_results=12):
    """
    Cerca prodotti su Amazon (pagina di ricerca HTML).
    Restituisce lista di dizionari con: title, url, asin, price (float o None), has_offer (bool)
    """
    results = []
    try:
        html = _fetch_search_page(keyword, country_code)
    except Exception as e:
        logger.exception("Errore fetch Amazon: %s", e)
        return results

    soup = BeautifulSoup(html, "lxml")
    # trovo i blocchi prodotto con data-asin
    items = soup.find_all("div", {"data-asin": True})
    for item in items:
        asin = item.get("data-asin", "").strip()
        if not asin:
            continue

        # titolo
        title_tag = item.select_one("h2 a span") or item.select_one("span.a-size-medium") or item.select_one("span.a-size-base-plus")
        title = title_tag.get_text().strip() if title_tag else None

        # link
        a = item.select_one("h2 a") or item.select_one("a.a-link-normal")
        url = None
        if a and a.get("href"):
            url = urljoin("https://www.amazon.it", a["href"])

        # prezzo
        price_whole = item.select_one("span.a-price-whole")
        price_frac = item.select_one("span.a-price-fraction")
        price = None
        if price_whole:
            try:
                # rimuove punti migliaia
                whole_text = price_whole.get_text().strip().replace(".", "").replace(",", "")
                frac_text = price_frac.get_text().strip() if price_frac else "00"
                price = float(f"{whole_text}.{frac_text}")
            except Exception:
                price = None

        # prezzo listino per calcolare sconto (se presente)
        list_price_tag = item.select_one("span.a-price.a-text-price span.a-offscreen")
        list_price = None
        if list_price_tag:
            ptext = list_price_tag.get_text().strip().replace("€", "").replace(".", "").replace(",", ".").strip()
            try:
                list_price = float(ptext)
            except Exception:
                list_price = None

        # stima sconto percentuale
        discount = None
        if price and list_price and list_price > 0:
            discount = round((list_price - price) / list_price * 100, 1)

        # has_offer = prezzo presente e discount>0 o prezzo presente e list_price present
        has_offer = (discount is not None and discount > 0) or (list_price is not None and price is not None and list_price > price)

        results.append({
            "asin": asin,
            "title": title,
            "url": url,
            "price": price,
            "list_price": list_price,
            "discount": discount,
            "has_offer": bool(has_offer),
        })

        if len(results) >= max_results:
            break

    return results
