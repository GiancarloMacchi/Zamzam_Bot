import telegram
import logging
import asyncio
from telegram.error import TelegramError

async def send_telegram_message(config, products_list, keyword):
    try:
        if not products_list:
            logging.info(f"Nessun prodotto trovato per: {keyword}")
            return
        
        bot = telegram.Bot(token=config["TELEGRAM_BOT_TOKEN"])
        
        for p in products_list:
            message = ""
            message += f"**🤩 {p['title']}**\n"
            message += f"Sconto: {p['discount']}% 🔥\n"
            message += f"Prezzo: {p['price']}€\n"
            message += f"Link: {p['url']}\n\n"
            
            try:
                if p.get('image'):
                    await bot.send_photo(
                        chat_id=config["TELEGRAM_CHAT_ID"],
                        photo=p['image'],
                        caption=message,
                        parse_mode='Markdown'
                    )
                else:
                    await bot.send_message(
                        chat_id=config["TELEGRAM_CHAT_ID"],
                        text=message,
                        parse_mode='Markdown'
                    )
            except TelegramError as te:
                logging.error(f"Errore di Telegram durante l'invio del post: {te}. Invio solo il testo.")
                await bot.send_message(
                    chat_id=config["TELEGRAM_CHAT_ID"],
                    text=message,
                    parse_mode='Markdown'
                )

            await asyncio.sleep(300) # Pausa di 5 minuti tra i post
        
        # Frase di chiusura
        ending_text = "✨ C'è una soluzione per ogni problema, e un gioco per ogni sorriso! Trova il tuo preferito per divertirti con René! ✨"
        await bot.send_message(
            chat_id=config["TELEGRAM_CHAT_ID"],
            text=ending_text,
            parse_mode='Markdown'
        )
        
        logging.info(f"Offerte inviate per la parola chiave: {keyword}")
        
    except Exception as e:
        logging.error(f"Errore generale in send_telegram_message: {e}")
