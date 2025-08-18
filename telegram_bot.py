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
        
        # Frase di introduzione personalizzata
        intro_message = f"🥳 Ciao a tutti! Oggi René e i suoi amici hanno trovato delle offerte super divertenti su Amazon!\n\n"
        
        # Invio del messaggio introduttivo
        await bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=intro_message, parse_mode='Markdown')
        
        for p in products_list:
            message = ""
            message += f"**🤩 {p['title']}**\n"
            message += f"Sconto: {p['discount']}% 🔥\n"
            message += f"Prezzo: {p['price']}€\n"
            message += f"Link: {p['url']}\n\n"
            
            # Invio del post con immagine e didascalia
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
                        text=f"{message}\n\n⚠️ Immagine non disponibile.",
                        parse_mode='Markdown'
                    )
            except TelegramError as te:
                logging.error(f"Errore di Telegram durante l'invio del post: {te}. Invio solo il testo.")
                await bot.send_message(
                    chat_id=config["TELEGRAM_CHAT_ID"],
                    text=message,
                    parse_mode='Markdown'
                )

            await asyncio.sleep(5)  # Pausa di 5 secondi tra i post per evitare limitazioni di Telegram
        
        logging.info(f"Offerte inviate per la parola chiave: {keyword}")
        
    except Exception as e:
        logging.error(f"Errore generale in send_telegram_message: {e}")
