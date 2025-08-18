import telegram
import logging
import asyncio
from telegram.error import TelegramError
import json
import random
import html

async def send_telegram_message(config, products_list, keyword):
    try:
        if not products_list:
            logging.info(f"Nessun prodotto trovato per: {keyword}")
            return
        
        try:
            with open('phrases.json', 'r') as f:
                phrases_data = json.load(f)
        except FileNotFoundError:
            logging.error("File 'phrases.json' non trovato.")
            phrases_data = {"kids": [], "default": []}

        bot = telegram.Bot(token=config["TELEGRAM_BOT_TOKEN"])
        
        for p in products_list:
            category_phrases = phrases_data.get("kids", []) if keyword in ["giocattoli", "bambini", "scuola", "piscina", "lego"] else phrases_data.get("default", [])
            random_phrase = random.choice(category_phrases) if category_phrases else "Un affare da non perdere!"
            
            # Sanitizza i titoli per prevenire problemi con il parsing HTML
            safe_title = html.escape(p['title'])
            
            message = ""
            message += f"<b>{random_phrase}</b>\n\n"
            message += f"<b>🤩 {safe_title}</b>\n"
            message += f"💰 Prezzo: <b>{p['price']}€</b>\n"
            message += f"🔥 Sconto: <b>{p['discount']}%</b>\n"
            message += f"🔗 Link: <b>{p['url']}</b>\n\n"
            
            try:
                if p.get('image'):
                    await bot.send_photo(
                        chat_id=config["TELEGRAM_CHAT_ID"],
                        photo=p['image'],
                        caption=message,
                        parse_mode='HTML',
                        disable_notification=True  # Disattiva la notifica
                    )
                else:
                    await bot.send_message(
                        chat_id=config["TELEGRAM_CHAT_ID"],
                        text=message,
                        parse_mode='HTML',
                        disable_notification=True  # Disattiva la notifica
                    )
            except TelegramError as te:
                logging.error(f"Errore di Telegram durante l'invio del post: {te}. Invio solo il testo.")
                await bot.send_message(
                    chat_id=config["TELEGRAM_CHAT_ID"],
                    text=message,
                    parse_mode='HTML',
                    disable_notification=True  # Disattiva la notifica
                )

            await asyncio.sleep(300)
        
        ending_text = "✨ C'è una soluzione per ogni problema, e un gioco per ogni sorriso! Trova il tuo preferito per divertirti con René! ✨"
        await bot.send_message(
            chat_id=config["TELEGRAM_CHAT_ID"],
            text=ending_text,
            parse_mode='HTML',
            disable_notification=True  # Disattiva la notifica
        )
        
        logging.info(f"Offerte inviate per la parola chiave: {keyword}")
        
    except Exception as e:
        logging.error(f"Errore generale in send_telegram_message: {e}")
