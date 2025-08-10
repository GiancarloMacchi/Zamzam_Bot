#!/usr/bin/env python3
# main.py - cerca offerte Amazon (PA-API) e posta su Telegram con link affiliato + shortener Bitly

import os
import sys
import time
import json
import logging
import requests
from typing import Optional

# opcionalmente carica .env in locale
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Amazon PA-API wrapper (usiamo la versione che hai installato)
from amazon_paapi import AmazonApi

# Scheduler (usiamo blocking scheduler solo se RUN_ONCE non è impostato)
from apscheduler.schedulers.blocking import BlockingScheduler

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="***%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)
log = logging.getLogger("post-deal")

# --- Helper per leggere ENV con fallback a nomi alternativi ---
def getenv_first(*names, default=None):
    for n in names:
        v = os.environ.get(n)
        if v is not None and v != "":
            return v
    return default

# --- CONFIG / ENV (tollerante ai nomi alternativi) ---
AMAZON_ACCESS_KEY = getenv_first("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = getenv_first("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = getenv_first("AMAZON_ASSOCIATE_TAG", "AMAZON_PARTNER_TAG")
AMAZON_COUNTRY = getenv_first("AMAZON_COUNTRY", "AMAZON_REGION", default=None)  # preferiamo AMAZON_COUNTRY
BITLY_TOKEN = getenv_first("BITLY_TOKEN", "BITLY")
KEYWORDS = getenv_first("KEYWORDS", "bambini,giochi,libri bambini,neonato,mamme,gravidanza,abbigliamento bambini")
MIN_SAVE = int(getenv_first("MIN_SAVE", "20") or 20)
ITEM_COUNT = int(getenv_first("ITEM_COUNT", "10") or 10)
TELEGRAM_BOT_TOKEN = getenv_first("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = getenv_first("TELEGRAM_CHAT_ID", None)
RUN_ONCE = getenv_first("RUN_ONCE", "true").lower() in ("1", "true", "yes")

# normalize keywords -> list
KEYWORDS = [k.strip() for k in KEYWORDS.split(",") if k.strip()]

# --- Controllo presenza secrets obbligatori ---
required_map = {
    "AMAZON_ACCESS_KEY": AMAZON_ACCESS_KEY,
    "AMAZON_SECRET_KEY": AMAZON_SECRET_KEY,
    "AMAZON_ASSOCIATE_TAG": AMAZON_ASSOCIATE_TAG,
    "AMAZON_COUNTRY": AMAZON_COUNTRY,
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
}

missing = [k for k, v in required_map.items() if not v]
if missing:
    raise ValueError(f"⚠️ Manca una o più variabili d'ambiente nei Secrets: {', '.join(missing)}")

log.info("Usando AMAZON_COUNTRY = %s (puoi cambiarlo nel Secret AMAZON_COUNTRY o AMAZON_REGION).", AMAZON_COUNTRY or "IT")

# --- Init Amazon client ---
try:
    amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY or "IT")
except Exception as e:
    log.exception("Errore inizializzazione AmazonApi:")
    sys.exit(1)

# --- Helper Bitly ---
def shorten_bitly(long_url: str) -> str:
    if not BITLY_TOKEN:
        return long_url
    try:
        headers = {
            "Authorization": f"Bearer {BITLY_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {"long_url": long_url}
        r = requests.post("https://api-ssl.bitly.com/v4/shorten", headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("link") or long_url
    except Exception as e:
        log.warning("Bitly shortening fallito: %s", e)
        return long_url

# --- Helper Telegram ---
def send_telegram_message(text: str) -> Optional[dict]:
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

def send_telegram_photo(photo_url: str, caption: str, button_url: Optional[str] = None) -> Optional[dict]:
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
    if button_url:
        payload["reply_markup"] = json.dumps({
            "inline_keyboard": [[{"text": "Acquista ora", "url": button_url}]]
        })
    try:
        r = requests.post(api, data=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning("Invio photo fallito, provo a inviare come messaggio. Errore: %s", e)
        if button_url:
            return send_telegram_message(f"{caption}\n\nAcquista: {button_url}")
        return send_telegram_message(caption)

# --- Funzioni utili ---
def ensure_affiliate_tag(url: str) -> str:
    if not url:
        return url
    tag = AMAZON_ASSOCIATE_TAG
    if not tag:
        return url
    if "tag=" in url or "associates" in url:
        return url
    if "?" in url:
        return f"{url}&tag={tag}"
    else:
        return f"{url}?tag={tag}"

def parse_saving(raw):
    """
    Raw può essere int, float, string con '%' o None. Torna int o 0.
    """
    if raw is None:
        return 0
    try:
        if isinstance(raw, (int, float)):
            return int(raw)
        s = str(raw).strip().replace("%", "")
        return int(float(s))
    except Exception:
        return 0

# --- Core: pick_deal (cerca e filtra per MIN_SAVE) ---
def pick_deal():
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
                # titolo
                title = getattr(getattr(it, "item_info", None), "title", None)
                if title:
                    title = getattr(title, "display_value", None) or str(title)
                title = title or "Prodotto Amazon"

                # immagine
                img = None
                try:
                    img = getattr(it.images.primary.large, "url", None)
                except Exception:
                    try:
                        img = getattr(it.images.primary, "url", None)
                    except Exception:
                        img = None

                # url
                url = getattr(it, "detail_page_url", None) or None

                # prezzo display
                price = None
                try:
                    price = it.offers.listings[0].price.display_amount
                except Exception:
                    try:
                        price = it.offers.listings[0].price.amount
                    except Exception:
                        price = None

                # percentuale di risparmio (più tentativi)
                saving_pct = None
                try:
                    saving_pct = getattr(it.offers.listings[0], "saving_percentage", None)
                    if saving_pct is None:
                        saving_pct = getattr(it.offers.listings[0].price, "savings_percentage", None)
                except Exception:
                    saving_pct = None

                saving_pct = parse_saving(saving_pct)
                # applichiamo soglia minima
                if saving_pct < MIN_SAVE:
                    continue

                score = saving_pct or 0
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
    saving = item.get("saving_pct") or 0
    url = item.get("url") or ""

    # tono in base allo sconto
    if saving >= 50:
        lead = "🔥 SUPER SCONTO!"
    elif saving >= 35:
        lead = "🔥 Ottimo sconto!"
    elif saving >= 20:
        lead = "✅ Buona offerta!"
    else:
        lead = "Offerta"

    lines = [f"{lead} <b>{title}</b>"]
    if price:
        lines.append(f"Prezzo: {price}")
    if saving:
        lines.append(f"Risparmio stimato: {saving}%")
    lines.append("")  # separazione
    lines.append("🔎 Descrizione rapida: prodotto selezionato per la tua nicchia")
    lines.append("")
    lines.append("(Link affiliato — grazie se acquisti con il mio codice!)")

    caption = "\n".join(lines)
    return caption[:1000]

def job_once():
    log.info("Job: avvio ricerca offerte...")
    deal, failed_keywords = pick_deal()
    if not deal:
        msg = f"Nessuna offerta trovata con sconto ≥ {MIN_SAVE}% (prova a ridurre MIN_SAVE o ampliare KEYWORDS)."
        log.info(msg)
        send_telegram_message(msg)
        return

    # prepara link affiliato + shortener
    url = deal.get("url")
    url = ensure_affiliate_tag(url)
    short = shorten_bitly(url)

    caption = make_caption(deal)

    if deal.get("img"):
        send_telegram_photo(deal["img"], caption, button_url=short)
    else:
        send_telegram_message(f"{caption}\n\n{short}")

    log.info("Fatto. Keyword fallite: %d", failed_keywords)

def main():
    try:
        if RUN_ONCE:
            job_once()
            return
        # se non RUN_ONCE, usiamo scheduler interno (utile per esecuzioni locali)
        sched = BlockingScheduler()
        sched.add_job(job_once, "interval", hours=1, next_run_time=None)
        log.info("Scheduler started (job ogni 1h). CTRL+C per fermare.")
        sched.start()
    except Exception as e:
        log.exception("Errore nel main:")
        send_telegram_message(f"Errore durante la ricerca o invio: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
