import logging
import time
import os
from amazon_api import search_amazon
from telegram_bot import send_telegram_message

# Logging a livello DEBUG per avere tutti i dettagli
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_config():
    return {
        'AMAZON_ACCESS_KEY': os.getenv('AMAZON_ACCESS_KEY'),
        'AMAZON_SECRET_KEY': os.getenv('AMAZON_SECRET_KEY'),
        'AMAZON_ASSOCIATE_TAG': os.getenv('AMAZON_ASSOCIATE_TAG'),
        'AMAZON_COUNTRY': os.getenv('AMAZON_COUNTRY', 'it'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'KEYWORDS': os.getenv('KEYWORDS', 'offerte del giorno').split(','),
        'MIN_SAVE': int(os.getenv('MIN_SAVE', 10)),
        'ITEM_COUNT': int(os.getenv('ITEM_COUNT', 5))
    }


def main():
    config = get_config()
    keywords = [kw.strip() for kw in config['KEYWORDS']]

    if not keywords:
        logging.warning("Nessuna parola chiave trovata. Il bot si ferma.")
        return

    logging.info("Avvio bot Amazon…")

    for keyword in keywords:
        logging.info(f"Cercando prodotti per: {keyword}")
        try:
            products = search_amazon(keyword, config)
            if products:
                message = f"✨ Offerte Amazon per **{keyword}** ✨\n\n"
                for p in products:
                    message += f"**{p['title']}**\n"
                    message += f"💰 Prezzo: {p['price']}€ (Sconto: {p['discount']}%)\n"
                    message += f"➡️ [Link all'offerta]({p['url']})\n\n"

                send_telegram_message(config, message)
                logging.info(f"Offerte inviate per la parola chiave: {keyword}")
            else:
                logging.info(f"Nessun prodotto trovato per: {keyword}")

        except Exception as e:
            logging.error(f"Errore durante l'esecuzione per la parola chiave '{keyword}': {e}")

        time.sleep(10)  # Pausa tra una ricerca e l'altra per evitare ban

    logging.info("Esecuzione completata.")


if __name__ == "__main__":
    main()
