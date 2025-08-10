#!/usr/bin/env python3
# main.py - cerca offerte su Amazon (PA-API) e le posta su Telegram
import os
import sys
import time
import logging
from typing import Optional, List

# opzionale per sviluppo locale (.env)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import requests
from amazon_paapi import AmazonApi  # wrapper usato nel progetto

# --- CONFIG / ENV ---
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")

# keywords più generiche nella nicchia genitori/bambini
KEYWORDS = os.environ.get(
    "KEYWORDS",
    "bambini,neonati,giocattoli,giochi,abbigliamento bambini,abbigliamento neonato,abbigliamento premaman,mamme,prima infanzia,libri bambini"
).split(",")

# MIN_SAVE richiesto (ora 20%)
MIN_SAVE = int(os.environ.get("MIN_SAVE", "20"))
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
        log.warning("Invio photo fallito, provo come messaggio. Errore: %s", e)
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

def extract_asin_from_search_item(it) -> Optional[str]:
    # proviamo alcuni attributi possibili
    for attr in ("asin", "asin_value", "ASIN", "asin"):
        v = getattr(it, attr, None)
        if v:
            return v
    # fallback: alcuni wrapper espongono item.asin.value
    try:
        v = getattr(getattr(it, "asin", None), "value", None)
        if v:
            return v
    except Exception:
        pass
    return None

def fetch_details_for_asins(asins: List[str]):
    """Chiama get_items per una lista di ASIN e ritorna la risposta (o None)."""
    if not asins:
        return None
    resources = [
        "Images.Primary.Large",
        "ItemInfo.Title",
        "Offers.Listings.Price",
        "Offers.Listings.SavingAmount",
        "Offers.Listings.SavingPercentage",
    ]
    try:
        # alcuni wrapper aspettano item_ids / item_id_list, proviamo la forma più comune
        details = amazon.get_items(item_ids=asins, resources=resources)
        return details
    except TypeError as e:
        log.warning("get_items TypeError con resources, riprovo senza resources: %s", e)
        try:
            details = amazon.get_items(item_ids=asins)
            return details
        except Exception as e2:
            log.warning("get_items fallback fallito: %s", e2)
            return None
    except Exception as e:
        log.warning("Errore get_items: %s", e)
        return None

def parse_saving_from_detail(d) -> Optional[float]:
    """Estrae la percentuale di saving da un item detail (se disponibile)."""
    try:
        # proviamo listing.saving_percentage
        sp = getattr(d.offers.listings[0], "saving_percentage", None)
        if sp is not None:
            return float(sp)
    except Exception:
        pass
    try:
        sp = getattr(getattr(d.offers.listings[0], "price", None), "savings_percentage", None)
        if sp is not None:
            return float(sp)
    except Exception:
        pass
    # in alcuni casi saving_amount + price => possiamo provare a calcolare, ma saltiamo per ora
    return None

def pick_deal():
    """Cerca tra le keywords e ritorna l'offerta con il maggior saving trovato (se disponibile)."""
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
        # raccogliamo ASIN trovati
        asins = []
        for it in items:
            asin = extract_asin_from_search_item(it)
            if asin:
                asins.append(asin)
        if not asins:
            # niente ASIN => saltiamo
            continue

        # prendiamo i dettagli (offers) per quegli ASIN
        details = fetch_details_for_asins(asins)
        detail_items = getattr(details, "items", []) or [] if details else []

        # se abbiamo dettagli, usiamoli
        for d in detail_items:
            try:
                # titolo
                title = getattr(getattr(d, "item_info", None), "title", None)
                if title:
                    title = getattr(title, "display_value", None) or str(title)
                else:
                    title = getattr(d, "title", None) or "Prodotto Amazon"

                # immagine
                img = None
                try:
                    img = getattr(d.images.primary.large, "url", None)
                except Exception:
                    try:
                        img = getattr(d.images.primary, "url", None)
                    except Exception:
                        img = None

                url = getattr(d, "detail_page_url", None) or f"https://www.amazon.{AMAZON_COUNTRY.lower()}/dp/{getattr(d, 'asin', '')}"

                # prezzo
                price = None
                try:
                    price = d.offers.listings[0].price.display_amount
                except Exception:
                    try:
                        price = d.offers.listings[0].price.amount
                    except Exception:
                        price = None

                # percentuale di risparmio
                saving_pct = parse_saving_from_detail(d)

                # filtriamo per soglia minima
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
                        "keyword": kw,
                        "asin": getattr(d, "asin", None),
                    }
            except Exception as e:
                log.debug("Ignoro dettaglio item per errore parsing: %s", e)
                continue

        # fallback: talvolta saving info è presente direttamente nell'oggetto di search
        if not best:
            for it in items:
                try:
                    # prova a leggere saving dalla search-item (se esiste)
                    saving_pct = None
                    try:
                        saving_pct = getattr(it.offers.listings[0], "saving_percentage", None)
                        if saving_pct is None:
                            saving_pct = getattr(getattr(it.offers.listings[0], "price", None), "savings_percentage", None)
                    except Exception:
                        saving_pct = None

                    if saving_pct is None or saving_pct < MIN_SAVE:
                        continue

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
    caption = "\n".join(lines)
    return caption[:1000]

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

        log.info(f"Pubblico: {deal['title']} (risparmio: {deal.get('saving_pct')})")
        send_telegram_photo(deal["img"], caption)
        log.info("Fatto. Keyword fallite: %d", failed_keywords)
    except Exception as e:
        log.exception("Errore durante la ricerca o invio:")
        send_telegram_message(f"Errore durante la ricerca o invio: {e}")

if __name__ == "__main__":
    main()
