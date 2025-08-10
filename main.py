import os
import logging
import utils

logging.basicConfig(level=logging.INFO)

def main():
    try:
        amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
        amazon_secret_key = os.getenv("AMAZON_SECRET_KEY")
        amazon_associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        amazon_country = os.getenv("AMAZON_COUNTRY")
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not all([amazon_access_key, amazon_secret_key, amazon_associate_tag, amazon_country, telegram_token, telegram_chat_id]):
            logging.error("Uno o più secrets mancanti.")
            return

        # Ricerca prodotti
        prodotti = utils.cerca_prodotti(
            amazon_access_key,
            amazon_secret_key,
            amazon_associate_tag,
            amazon_country
        )

        for prodotto in prodotti:
            try:
                if not utils.ha_offerte(prodotto):
                    continue
                if not utils.filtro_categoria(prodotto):
                    continue
                if not utils.filtro_sconto(prodotto, 20):
                    continue
                if not utils.filtro_lingua(prodotto, "it"):
                    continue

                messaggio = utils.formatta_messaggio(prodotto)
                utils.invia_telegram(telegram_token, telegram_chat_id, messaggio)

            except Exception as e:
                logging.error(f"Errore con il prodotto {prodotto.get('ASIN', 'N/D')}: {e}")

    except Exception as e:
        logging.error(f"Errore generale: {e}")

if __name__ == "__main__":
    main()
