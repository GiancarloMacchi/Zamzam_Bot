import os
import logging
import asyncio
import telegram
from datetime import datetime

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

from amazon_api import search_amazon
from telegram_bot import send_telegram_message

async def main():
    logging.info("Avvio bot Amazon…")
    
    for keyword in config['KEYWORDS']:
        try:
            products = search_amazon(keyword, config)
            if products:
                await send_telegram_message(config, products, keyword)
            
            # Pausa di 60 secondi tra le parole chiave per non stressare l'API di Amazon
            await asyncio.sleep(60)
            
        except Exception as e:
            logging.error(f"Errore generale per la parola chiave {keyword}: {e}")
            
    logging.info("Esecuzione completata.")

async def run_bot_loop():
    bot = telegram.Bot(token=config["TELEGRAM_BOT_TOKEN"])
    
    while True:
        now = datetime.now()
        
        # Calcola il tempo rimanente fino alle 7:30
        if now.hour < 7 or (now.hour == 7 and now.minute < 30):
            # Calcola i secondi rimanenti
            next_run = now.replace(hour=7, minute=30, second=0, microsecond=0)
            wait_seconds = (next_run - now).total_seconds()
            logging.info(f"Il bot si mette a riposo fino alle 7:30. Riprenderà tra {int(wait_seconds/60)} minuti.")
            await asyncio.sleep(wait_seconds)
        
            # Invia il messaggio introduttivo una sola volta al mattino
            intro_message = f"🥳 **Ecco le migliori offerte di René per oggi!**\n\n"
            await bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=intro_message, parse_mode='Markdown')

        await main()
        
        # Dopo le 23:59, il bot attende il giorno dopo
        if now.hour >= 23 and now.minute >= 59:
             wait_seconds = (now.replace(hour=7, minute=30, second=0, day=now.day+1) - now).total_seconds()
             logging.info(f"Il bot si mette a riposo notturno. Riprenderà tra {int(wait_seconds/60)} minuti.")
             await asyncio.sleep(wait_seconds)


if __name__ == "__main__":
    if config['RUN_ONCE']:
        asyncio.run(main())
    else:
        asyncio.run(run_bot_loop())
