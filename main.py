#!/usr/bin/env python3
# main.py - cerca offerte Amazon (PA-API) e le posta su Telegram con pulsante affiliato

import os
import sys
import time
import logging
import requests
from typing import Optional
from urllib.parse import urlencode
from amazon_paapi import AmazonApi

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# --- CONFIG ---
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")
KEYWORDS = ["bambini", "giochi", "mamma", "neonato", "passeggino", "libri bambini", "gravidanza", "scuola"]
MIN_SAVE = int(os.environ.get("MIN_SAVE", "20"))
ITEM_COUNT = int(os.environ.get("ITEM_COUNT", "10"))

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

BITLY_TOKEN = os.environ.get("BITLY_TOKEN")  # opzionale per shortlink professionali

logging.basicConfig(
    level=logging.INFO,
    format="***%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)
log = logging.getLogger("post-deal")

# --- Short link generator ---
def shorten_url(url):
    """Accorcia l'URL usando Bitly (se token presente) o TinyURL."""
    try:
        if BITLY_TOKEN:
            r = requests.post(
                "https://api-ssl.bitly.com/v4/shorten",
                headers={"Authorization": f"Bearer {BITLY_TOKEN}"},
                json={"long_url": url},
                timeout=10
            )
            if r.status_code == 200:
                return r.json().get("link", url)
        else:
            r = requests.get(f"http://tinyurl.com/api-create.php?{urlencode({'url': url})}", timeout=10)
            if r.status_code == 200:
                return r.text.strip()
    except Exception as e:
        log.warning("Errore accorciamento link: %s", e)
    return url

# --- Telegram helpers ---
def send_telegram_photo_with_button(photo_url: str, caption: str, button_url: str):
    """Invia foto con pulsante inline su Telegram."""
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": photo_url,
        "caption": caption[:1000],
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🛒 Compra ora", "url": button_url}]
            ]
        }
    }
    try:
        r = requests.post(api, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.exception("Errore invio messaggio con pulsante:")
        return None

# --- Amazon API ---
if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG]):
    raise ValueError("⚠️ Manca una o più variabili AMAZON_* nei Secrets!")

try:
    amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
except Exception as e:
    log.exception("Errore inizializzazione AmazonApi:")
    sys.exit(1)

# --- Deal Picker ---
def pick_deal():
    """Trova l'offerta con sconto >= MIN_SAVE nelle categorie selezionate."""
    best = None
    for kw in KEYWORDS:
        kw = kw.strip()
        if not kw:
            continue
        log.info("🔎 Cerco: %s", kw)
        try:
            res = amazon.search_items(keywords=kw, item_count=ITEM_COUNT)
        except Exception as e:
            log.warning("❌ Errore ricerca '%s': %s", kw, e)
            time.sleep(1)
            continue

        items = getattr(res, "items", []) or []
        for it in items:
            try:
                saving_pct = getattr(it.offers.listings[0], "saving_percentage", None) or 0
                if saving_pct < MIN_SAVE:
                    continue
                title = getattr(it.item_info.title, "display_value", "Prodotto Amazon")
                img = getattr(it.images.primary.large, "url", None)
                url = getattr(it, "detail_page_url", None)
                price = getattr(it.offers.listings[0].price, "display_amount", None)
                if best is None or saving_pct > best["saving_pct"]:
                    best = {
                        "title": title,
                        "img": img,
                        "url": url,
                        "price": price,
                        "saving_pct": saving_pct
                    }
            except:
                continue
    return best

# --- Caption generator ---
def generate_caption(item):
    """Genera testo descrittivo personalizzato per l'offerta."""
    title = item["title"]
    price = item["price"] or ""
    saving = item["saving_pct"]
    # frase personalizzata
    custom_line = f"Ideale per la tua famiglia! Approfitta subito di questo sconto del {saving}%."
    lines = [
        f"🔥 <b>{title}</b>",
        f"Prezzo: {price}",
        custom_line
    ]
    return "\n".join(lines)

# --- Main ---
def main():
    deal = pick_deal()
    if not deal:
        log.info("Nessuna offerta trovata.")
        return

    caption = generate_caption(deal)
    affiliate_url = f"{deal['url']}&tag={AMAZON_ASSOCIATE_TAG}"
    short_url = shorten_url(affiliate_url)
    send_telegram_photo_with_button(deal["img"], caption, short_url)
    log.info("✅ Offerta pubblicata: %s", deal["title"])

if __name__ == "__main__":
    main()
