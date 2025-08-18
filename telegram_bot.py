import telegram
import logging
import time
import asyncio

async def send_telegram_message(config, products_list, keyword):
    try:
        if not products_list:
            logging.info(f"Nessun prodotto trovato per: {keyword}")
            return
        
        bot = telegram.Bot(token=config["TELEGRAM_BOT_TOKEN"])
        
        message = f"**🔥 Super Offerte su Amazon - {keyword.capitalize()} 🔥**\n\n"
        
        for p in products_list:
            message += f"**{p['title']}**\n"
            message += f"Sconto: {p['discount']}%\n"
            message += f"Prezzo: {p['price']}€\n"
            message += f"Link: {p['url']}\n\n"
        
        logging.debug(f'Set Bot API URL: {bot.base_url}')
        logging.debug(f'Set Bot API File URL: {bot.base_file_url}')

        await bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=message, parse_mode='Markdown')
        
        logging.info("Messaggio inviato su Telegram")
        
    except Exception as e:
        logging.error(f"Errore durante l'invio del messaggio Telegram: {e}")
