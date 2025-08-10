import os
import requests
from amazon_paapi import AmazonApi
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import random

# ===== CONFIG =====
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
BITLY_TOKEN = os.environ.get("BITLY_TOKEN")

if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BITLY_TOKEN]):
    raise ValueError("⚠️ Manca una o più variabili d'ambiente richieste nei Secrets!")

amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
bot = Bot(token=TELEGRAM_TOKEN)

# ===== FUNZIONI =====

def genera_messaggio_prodotto(titolo, prezzo, prezzo_offerta, sconto):
    if sconto >= 50:
        frasi = [
            f"🔥 SUPER AFFARE! {titolo} ora a soli {prezzo_offerta}€ (sconto {sconto}%, prima {prezzo}€)!",
            f"💥 OFFERTA IMPERDIBILE: {titolo} con il {sconto}% di sconto! Solo {prezzo_offerta}€!"
        ]
    elif 30 <= sconto < 50:
        frasi = [
            f"😊 Ottima occasione: {titolo} a {prezzo_offerta}€ (sconto {sconto}%, prima {prezzo}€).",
            f"👌 Non lasciartelo scappare: {titolo} scontato del {sconto}%!"
        ]
    else:
        frasi = [
            f"😉 Piccolo sconto ma ottimo acquisto: {titolo} a {prezzo_offerta}€ (prima {prezzo}€).",
            f"📚 Approfitta: {titolo} ora a {prezzo_offerta}€, sconto {sconto}%."
        ]
    return random.choice(frasi)

def accorcia_link_bitly(url):
    headers = {"Authorization": f"Bearer {BITLY_TOKEN}", "Content-Type": "application/json"}
    data = {"long_url": url}
    resp = requests.post("https://api-ssl.bitly.com/v4/shorten", json=data, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("link")
    else:
        print(f"Errore Bitly: {resp.text}")
        return url

def trova_offerte():
    keywords = ["bambini", "giocattoli", "neonati", "mamme", "prima infanzia", "passeggini", "libri bambini"]
    risultati_finali = []

    for kw in keywords:
        print(f"🔍 Ricerca per keyword: {kw}")
        try:
            prodotti = amazon.search_products(keywords=kw, search_index="All", item_count=30)
        except Exception as e:
            print(f"Errore API Amazon: {e}")
            continue

        for p in prodotti:
            try:
                prezzo_listino = float(p.list_price.amount) if p.list_price else None
                prezzo_offerta = float(p.offer_price.amount) if p.offer_price else None

                if not prezzo_listino or not prezzo_offerta:
                    continue

                sconto = round((prezzo_listino - prezzo_offerta) / prezzo_listino * 100, 1)
                if sconto >= 20:
                    risultati_finali.append({
                        "titolo": p.title,
                        "prezzo": prezzo_listino,
                        "prezzo_offerta": prezzo_offerta,
                        "sconto": sconto,
                        "url": p.detail_page_url
                    })
            except Exception:
                continue

    return risultati_finali

# ===== MAIN =====

offerte = trova_offerte()

if offerte:
    offerta_scelta = random.choice(offerte)
    print(f"✅ Offerta trovata: {offerta_scelta['titolo']} - Sconto {offerta_scelta['sconto']}%")

    # Accorcia link
    short_url = accorcia_link_bitly(offerta_scelta['url'])

    # Messaggio personalizzato
    messaggio = genera_messaggio_prodotto(
        offerta_scelta['titolo'],
        offerta_scelta['prezzo'],
        offerta_scelta['prezzo_offerta'],
        offerta_scelta['sconto']
    )

    # Pulsante
    button = [[InlineKeyboardButton("🛒 Vai all'offerta", url=short_url)]]
    reply_markup = InlineKeyboardMarkup(button)

    # Invia messaggio
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, reply_markup=reply_markup)

else:
    print("❌ Nessuna offerta trovata con almeno il 20% di sconto.")
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Oggi niente offerte interessanti 😢")
