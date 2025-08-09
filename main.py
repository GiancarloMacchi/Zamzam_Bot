#!/usr/bin/env python3
# main.py - cerca offerte su Amazon (PA-API) e le posta su Telegram

import os, sys, requests
from amazon_paapi import AmazonApi

# ---------- configurazione da env (GitHub Secrets) ----------
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

KEYWORDS = os.environ.get("KEYWORDS", "cuffie,smartwatch,aspirapolvere,auricolari").split(",")
MIN_SAVE = int(os.environ.get("MIN_SAVE", "20"))    # percentuale minima di risparmio
ITEM_COUNT = int(os.environ.get("ITEM_COUNT", "8")) # numero di item per keyword

# check minimi
required = [AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
if not all(required):
    print("Errore: mancano variabili d'ambiente (controlla i Secrets su GitHub).")
    sys.exit(1)

# crea client Amazon
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY, throttling=1.0)

# risorse richieste: immagini, titolo, prezzo, sconto
RESOURCES = [
    "Images.Primary.Large",
    "ItemInfo.Title",
    "Offers.Listings.Price",
    "Offers.Listings.SavingAmount",
    "Offers.Listings.SavingPercentage",
]

def pick_deal():
    """Cerca tra le keywords e ritorna l'offerta con il maggior saving trovato."""
    best = None
    for kw in KEYWORDS:
        kw = kw.strip()
        try:
            res = amazon.search_items(
                keywords=kw,
                item_count=ITEM_COUNT,
                min_saving_percent=MIN_SAVE,
                resources=RESOURCES  # passato solo UNA volta
            )
        except Exception as e:
            print(f"[WARN] errore ricerca '{kw}': {e}")
            continue

        items = getattr(res, "items", []) or []
        for it in items:
            try:
                title = getattr(it.item_info.title, "display_value", None) or "Prodotto Amazon"
                img = getattr(it.images.primary.large, "url", None)
                url = getattr(it, "detail_page_url", None)

                # prezzo
                try:
                    price = it.offers.listings[0].price.display_amount
                except Exception:
                    price = getattr(it.offers.listings[0].price, "amount", None)

                # percentuale di risparmio
                saving_pct = None
                try:
                    saving_pct = getattr(it.offers.listings[0], "saving_percentage", None)
                    if saving_pct is None:
                        saving_pct = getattr(it.offers.listings[0].price, "savings_percentage", None)
                except Exception:
                    saving_pct = None

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
    return best

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
    return "\n".join(lines)[:1000]  # limite Telegram ~1024

def post_photo(photo_url, caption):
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}
    resp = requests.post(api, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    deal = pick_deal()
    if not deal:
        print("Nessuna offerta trovata (prova a ridurre MIN_SAVE o ampliare KEYWORDS).")
        return
    caption = make_caption(deal)
    if not deal.get("img"):
        print("Offerta trovata ma senza immagine, pubblico solo testo.")
        return
    print(f"Pubblico: {deal['title']} (risparmio: {deal.get('saving_pct')})")
    post_photo(deal["img"], caption)
    print("Fatto.")

if __name__ == "__main__":
    main()
