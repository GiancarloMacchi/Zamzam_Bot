#!/usr/bin/env python3
# main.py - cerca offerte su Amazon (PA-API) e le posta su Telegram
# Workaround: non passiamo "resources" alla libreria (evita il bug),
# e prendiamo immagine/titolo direttamente dalla pagina prodotto (og:image / og:title).

import os, sys, time, random, requests, re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from amazon_paapi import AmazonApi
from bs4 import BeautifulSoup

# ---------- configurazione da env (GitHub Secrets) ----------
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

KEYWORDS = os.environ.get("KEYWORDS", "cuffie,smartwatch,aspirapolvere,auricolari").split(",")
MIN_SAVE = int(os.environ.get("MIN_SAVE", "20"))    # percentuale minima (se supportata)
ITEM_COUNT = int(os.environ.get("ITEM_COUNT", "6")) # meno item per query per limitare rate

# check minimi
required = [AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
if not all(required):
    print("Errore: mancano variabili d'ambiente (controlla i Secrets su GitHub).")
    sys.exit(1)

# crea client Amazon (aumenta throttling se ricevi "Requests limit reached")
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY, throttling=2.0)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

def add_affiliate_tag(url):
    """Aggiunge il parametro tag=<associate_tag> all'URL se non presente."""
    if not url:
        return None
    try:
        p = urlparse(url)
        qs = parse_qs(p.query)
        if 'tag' in qs and qs['tag']:
            return url
        qs['tag'] = [AMAZON_ASSOCIATE_TAG]
        new_q = urlencode(qs, doseq=True)
        new_p = p._replace(query=new_q)
        return urlunparse(new_p)
    except Exception:
        # fallback semplice
        if '?' in url:
            return url + '&tag=' + AMAZON_ASSOCIATE_TAG
        else:
            return url + '?tag=' + AMAZON_ASSOCIATE_TAG

def scrape_image_and_title(detail_url):
    """Scarica la pagina prodotto e prova a estrarre og:image e og:title."""
    try:
        r = requests.get(detail_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        img_tag = soup.find("meta", property="og:image") or soup.find("meta", {"name": "twitter:image"})
        title_tag = soup.find("meta", property="og:title") or soup.find("meta", {"name": "twitter:title"})
        image = img_tag["content"].strip() if (img_tag and img_tag.get("content")) else None
        title = title_tag["content"].strip() if (title_tag and title_tag.get("content")) else None
        if not title:
            t = soup.find("title")
            if t:
                title = t.get_text().strip()
        return image, title
    except Exception:
        return None, None

def pick_deal():
    """Cerca tra le keywords e ritorna la prima offerta valida con immagine."""
    # Nota: non passiamo 'resources' (workaround del bug della libreria)
    for kw in KEYWORDS:
        kw = kw.strip()
        try:
            # min_saving_percent potrebbe essere ignorato se la libreria non espone i campi,
            # ma proviamo a usarlo comunque: se causa errori, rimuovilo in seguito.
            res = amazon.search_items(keywords=kw, item_count=ITEM_COUNT, min_saving_percent=MIN_SAVE)
        except Exception as e:
            print(f"[WARN] errore ricerca '{kw}': {e}")
            # se ricevi rate-limit, aumenta throttling o diminuisci ITEM_COUNT / KEYWORDS
            time.sleep(1.0)
            continue

        items = getattr(res, "items", []) or []
        for s in items:
            # prova a prendere detail_page_url o asin
            detail_url = getattr(s, "detail_page_url", None)
            asin = getattr(s, "asin", None) or getattr(s, "asin_value", None)
            # se manca url, prova a costruirlo da ASIN
            if not detail_url and asin:
                detail_url = f"https://www.amazon.{AMAZON_COUNTRY.lower()}/dp/{asin}"
            if not detail_url:
                continue

            # aggiungi tag affiliato al link
            tracked_url = add_affiliate_tag(detail_url)

            # fetch immagine e titolo dalla pagina
            image, title = scrape_image_and_title(detail_url)
            if not image:
                # se non trovi immagine, salta
                continue

            # per prezzo/saving: la pagina può essere più difficile da parsare; omettiamo se non disponibile
            price = None
            saving_pct = None

            return {
                "title": title or "Prodotto Amazon",
                "img": image,
                "url": tracked_url,
                "price": price,
                "saving_pct": saving_pct,
                "keyword": kw,
                "asin": asin
            }
    return None

def make_caption(item):
    title = item.get("title")
    price = item.get("price") or ""
    saving = item.get("saving_pct")
    url = item.get("url") or ""
    lines = [f"🔥 <b>{title}</b>"]
    if price:
        lines.append(f"Prezzo: {price}")
    if saving:
        lines.append(f"Risparmio stimato: {saving}%")
    if url:
        lines.append(f"\n🛒 Compra qui: {url}")
    lines.append("\n(Questo è un link affiliato — grazie se acquisti con il mio codice!)")
    return "\n".join(lines)[:1000]

def post_photo(photo_url, caption):
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}
    resp = requests.post(api, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    deal = pick_deal()
    if not deal:
        print("Nessuna offerta trovata (prova a ridurre MIN_SAVE o ampliare KEYWORDS, o aumenta throttling).")
        return
    caption = make_caption(deal)
    if not deal.get("img"):
        print("Offerta trovata ma senza immagine, pubblico solo testo (opzione migliorabile).")
        return
    print(f"Pubblico: {deal['title']} (asin: {deal.get('asin')})")
    try:
        post_photo(deal["img"], caption)
        print("Fatto.")
    except Exception as e:
        print("Errore invio Telegram:", e)

if __name__ == "__main__":
    main()
