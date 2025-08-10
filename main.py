#!/usr/bin/env python3
# main.py - cerca offerte su Amazon (PA-API) e le posta su Telegram
import os
import sys
import time
import logging
from typing import Optional

# opzionale per sviluppo locale (.env)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import requests
from amazon_paapi import AmazonApi  # la libreria installata dal repo git

# --- CONFIG / ENV ---
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")  # CORRETTO: AMAZON_COUNTRY
KEYWORDS = os.environ.get("KEYWORDS", "cuffie,smartwatch,aspirapolvere,auricolari").split(",")
MIN_SAVE = int(os.environ.get("MIN_SAVE", "20"))  # filtro minimo sconto
ITEM_COUNT = int(os.environ.get("ITEM_COUNT", "8"))

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="***%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)
log = logging.getLogger("post-deal")

# --- Helper Telegram ---
def send_telegram_message(text: str) -> Optional[dict]:
    """Invia messaggio di testo su Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram non configurato: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti.")
        return None
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(api, data=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.exception("Errore invio messaggio Telegram:")
        return None

def send_telegram_photo(photo_url: str, caption: str) -> Optional[dict]:
    """Invia foto via sendPhoto; fallback a sendMessage se fallisce."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram non configurato: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti.")
        return None
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": photo_url,
        "caption": caption[:1000],
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(api, data=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning("Invio photo fallito, provo a inviare come messaggio. Errore: %s", e)
        return send_telegram_message(caption)

# --- Validazione env ---
if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG]):
    raise ValueError("⚠️ Manca una o più variabili AMAZON_* nei Secrets di GitHub!")

# --- Init Amazon client ---
try:
    amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
except Exception as e:
    log.exception("Errore inizializzazione AmazonApi:")
    send_telegram_message(f"Errore init AmazonApi: {e}")
    sys.exit(1)

def pick_deal():
    """Cerca tra le keywords e ritorna l'offerta con il maggior saving sopra MIN_SAVE."""
    best = None
    failed_keywords = 0

    for kw in KEYWORDS:
        kw = kw.strip()
        if not kw:
            continue
        log.info("🔎 Cerco: %s", kw)
        try:
            res = amazon.search_items(keywords=kw, item_count=ITEM_COUNT)
        except Exception as e:
            log.warning("❌ Errore ricerca '%s': %s", kw, e)
            failed_keywords += 1
            time.sleep(1.0)
            continue

        items = getattr(res, "items", []) or []
        for it in items:
            try:
                title = getattr(it.item_info.title, "display_value", None) or "Prodotto Amazon"
                img = None
                try:
                    img = getattr(it.images.primary.large, "url", None)
                except Exception:
                    try:
                        img = getattr(it.images.primary, "url", None)
                    except Exception:
                        img = None
                url = getattr(it, "detail_page_url", None)
                price = None
                try:
                    price = it.offers.listings[0].price.display_amount
                except Exception:
                    try:
                        price = it.offers.listings[0].price.amount
                    except Exception:
                        price = None
                # percentuale di risparmio
                saving_pct = None
                try:
                    saving_pct = getattr(it.offers.listings[0], "saving_percentage", None)
                    if saving_pct is None:
                        saving_pct = getattr(it.offers.listings[0].price, "savings_percentage", None)
                except Exception:
                    saving_pct = None

                # FILTRO sconto minimo
                if saving_pct is None or saving_pct < MIN_SAVE:
                    continue

                score = saving_pct
                if best is None or (score and score > (best.get("saving_pct") or 0)):
                    best = {
                        "title": title,
                        "img": img,
                        "url": url,
                        "price": price,
                        "saving_pct": score,
                        "keyword": kw
                    }
            except Exception:
                continue

    return best, failed_keywords

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

def main():
    try:
        deal, failed_keywords = pick_deal()
        if not deal:
            msg = f"Nessuna offerta trovata con sconto ≥ {MIN_SAVE}%."
            log.info(msg)
            send_telegram_message(msg)
            return

        caption = make_caption(deal)
        if not deal.get("img"):
            log.info("Offerta trovata ma senza immagine, pubblico solo testo.")
            send_telegram_message(caption)
            return

        log.info(f"Pubblico: {deal['title']} (risparmio: {deal.get('saving_pct')}%)")
        send_telegram_photo(deal["img"], caption)
        log.info("Fatto. Keyword fallite: %d", failed_keywords)
    except Exception as e:
        log.exception("Errore durante la ricerca o invio:")
        send_telegram_message(f"Errore durante la ricerca o invio: {e}")

if __name__ == "__main__":
    main()
