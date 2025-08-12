import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
import requests

# Carica variabili d'ambiente (anche se usi GitHub Secrets, serve per debug locale)
load_dotenv()

# Credenziali Amazon PAAPI (da GitHub Secrets)
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Altri parametri
KEYWORDS = os.getenv("KEYWORDS", "iPhone")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inizializza client Amazon PAAPI
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)


def cerca_prodotti():
    """
    Cerca prodotti su Amazon usando python-amazon-paapi e filtra per sconto minimo.
    """
    try:
        results = amazon.search_items(
            keywords=KEYWORDS,
            search_index="All",
            item_count=ITEM_COUNT
        )
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
        return []

    prodotti_filtrati = []

    for prodotto in results.items:
        titolo = prodotto.item_info.title.display_value if prodotto.item_info and prodotto.item_info.title else "N/D"
        prezzo_offerta = (
            prodotto.offers.listings[0].price.amount
            if prodotto.offers and prodotto.offers.listings
            else None
        )
        prezzo_listino = (
            prodotto.offers.listings[0].price.savings.amount + prezzo_offerta
            if prodotto.offers and prodotto.offers.listings and prodotto.offers.listings[0].price.savings
            else None
        )

        if prezzo_listino and prezzo_offerta:
            sconto = round((prezzo_listino - prezzo_offerta) / prezzo_listino * 100, 2)
        else:
            sconto = 0

        if sconto >= MIN_SAVE:
            prodotti_filtrati.append({
                "titolo": titolo,
                "prezzo": prezzo_offerta if prezzo_offerta else "N/D",
                "prezzo_listino": prezzo_listino if prezzo_listino else "N/D",
                "sconto": sconto,
                "link": prodotto.detail_page_url
            })

    return prodotti_filtrati


def invia_telegram(messaggio):
    """
    Invia un messaggio su Telegram.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token o Chat ID Telegram mancanti.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"Errore Telegram: {r.text}")
    except Exception as e:
        print(f"Errore invio Telegram: {e}")


if __name__ == "__main__":
    prodotti = cerca_prodotti()

    if prodotti:
        for p in prodotti:
            messaggio = (
                f"<b>{p['titolo']}</b>\n"
                f"Prezzo: {p['prezzo']} €\n"
                f"Prezzo di listino: {p['prezzo_listino']} €\n"
                f"Sconto: {p['sconto']}%\n"
                f"<a href='{p['link']}'>Acquista qui</a>"
            )
            invia_telegram(messaggio)
    else:
        invia_telegram("❌ Nessun prodotto trovato con i criteri impostati.")
