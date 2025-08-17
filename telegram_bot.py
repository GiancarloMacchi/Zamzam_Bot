import logging
import time

def send_messages_with_interval(products, interval_minutes=30, DRY_RUN=True):
    for product in products:
        message = f"🔹 <b>{product['title']}</b>\n{product['url']}\n💰 Prezzo: {product['price']}\n{product['description']}\nImmagine: {product['image']}"
        if DRY_RUN:
            logging.info(f"[DRY RUN] Messaggio Telegram:\n{message}")
        else:
            # Inserisci qui il codice reale per inviare su Telegram
            pass
        logging.info(f"Attendo {interval_minutes} minuti prima della prossima offerta...")
        time.sleep(interval_minutes * 60)
