import os
import json
import logging
import requests

log = logging.getLogger("telegram_bot")
log.setLevel(logging.INFO)

# Legge i secrets / env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")  # opzionale, per accorciare i link

def shorten_bitly(long_url: str) -> str:
    """Accorcia il link con Bitly se BITLY_TOKEN è presente. Altrimenti ritorna long_url."""
    if not BITLY_TOKEN or not long_url:
        return long_url
    try:
        url = "https://api-ssl.bitly.com/v4/shorten"
        headers = {"Authorization": f"Bearer {BITLY_TOKEN}", "Content-Type": "application/json"}
        payload = {"long_url": long_url}
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        if r.ok:
            data = r.json()
            return data.get("link") or long_url
        log.warning("Bitly returned %s: %s", r.status_code, r.text)
    except Exception as e:
        log.exception("Errore Bitly: %s", e)
    return long_url

def send_telegram_message(text: str, disable_web_page_preview: bool = True) -> dict | None:
    """Invia un messaggio di testo su Telegram. Ritorna il JSON della risposta o None."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram non configurato (manca TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID).")
        return None
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true" if disable_web_page_preview else "false",
    }
    try:
        r = requests.post(api, data=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.exception("Errore invio messaggio Telegram: %s", e)
        return None

def send_telegram_photo(photo_url: str, caption: str, buy_url: str | None = None) -> dict | None:
    """
    Invia una foto con caption e, se passato buy_url, aggiunge un pulsante inline 'Compra ora'.
    Fall back a send_telegram_message se sendPhoto fallisce.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram non configurato (manca TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID).")
        return None

    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": photo_url,
        "caption": caption[:1000],
        "parse_mode": "HTML",
    }

    if buy_url:
        try:
            short = shorten_bitly(buy_url)
            reply_markup = {"inline_keyboard": [[{"text": "Compra ora", "url": short}]]}
            payload["reply_markup"] = json.dumps(reply_markup)
        except Exception:
            log.exception("Errore nella generazione del reply_markup (Bitly o json).")

    try:
        r = requests.post(api, data=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.exception("sendPhoto fallito, provo invio come messaggio. Errore: %s", e)
        # fallback: invia il caption come messaggio
        fallback_text = caption
        if buy_url:
            fallback_text += f"\n\n🛒 {buy_url}"
        return send_telegram_message(fallback_text)
