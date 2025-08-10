import os
import requests
import logging

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(text, chat_id):
    """
    Invia un messaggio di testo a Telegram con formattazione Markdown.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Messaggio inviato a Telegram")
    except Exception as e:
        logging.error(f"Errore nell'invio del messaggio Telegram: {e}")

def get_discount_percentage(product):
    """
    Calcola lo sconto in percentuale da un prodotto Amazon.
    Restituisce None se non disponibile.
    """
    try:
        if not hasattr(product, "offers") or not product.offers:
            return None

        offer = product.offers[0]  # Prende la prima offerta disponibile
        if hasattr(offer, "list_price") and hasattr(offer, "price"):
            list_price = offer.list_price.amount
            current_price = offer.price.amount
            if list_price and current_price and list_price > current_price:
                discount = round(((list_price - current_price) / list_price) * 100)
                return discount
        return None
    except Exception as e:
        logging.error(f"Errore nel calcolo dello sconto: {e}")
        return None
