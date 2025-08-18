import os
import logging
import asyncio

from amazon_api import search_amazon
from telegram_bot import send_telegram_message

# Configurazione del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variabili di configurazione lette dalle Secrets
config = {
    'AMAZON_ACCESS_KEY': os.environ.get('AMAZON_ACCESS_KEY'),
    'AMAZON_SECRET_KEY': os.environ.get('AMAZON_SECRET_KEY'),
    'AMAZON_ASSOCIATE_TAG': os.environ.get('AMAZON_ASSOCIATE_TAG'),
    'AMAZON_COUNTRY': os.environ.get('AMAZON_COUNTRY'),
    'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN'),
    'TELEGRAM_CHAT_ID': os.environ.get('TELEGRAM_CHAT_ID'),
    'KEYWORDS': os.environ.get('KEYWORDS').split(','),
    'MIN_SAVE': int(os.environ.get('MIN_SAVE')),
    'RUN_ONCE': os.environ.get('RUN_ONCE', 'false').lower() == 'true',
    'ITEM_COUNT': int(os.environ.get('ITEM_COUNT'))
}

async def main():
    logging.info("Avvio bot Amazon…")
    
    for keyword in config['KEYWORDS']:
        try:
            products = search_amazon(keyword, config)
            if products:
                # La logica di invio è ora in telegram_bot.py
                await send_telegram_message(config, products, keyword)
            
            # Pausa di 60 secondi tra le parole chiave per non stressare l'API di Amazon
            await asyncio.sleep(60)
            
        except Exception as e:
            logging.error(f"Errore generale per la parola chiave {keyword}: {e}")
            
    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    if config['RUN_ONCE']:
        asyncio.run(main())
    else:
        while True:
            asyncio.run(main())
            await asyncio.sleep(3600) # Pausa di 1 ora per le esecuzioni successive
