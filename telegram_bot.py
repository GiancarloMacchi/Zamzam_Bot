import telegram
import logging
import asyncio
from telegram.error import TelegramError
import json
import random

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

            message = ""
            message += f"{random_phrase}\n\n"
            message += f"**🤩 {p['title']}**\n"
            message += f"💰 Prezzo: **{p['price']}€**\n"
            message += f"🔥 Sconto: **{p['discount']}%**\n"
            message += f"🔗 Link: **{p['url']}**\n\n"
            
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

            await asyncio.sleep(300)
        
        ending_text = "✨ C'è una soluzione per ogni problema, e un gioco per ogni sorriso! Trova il tuo preferito per divertirti con René! ✨"
        await bot.send_message(
            chat_id=config["TELEGRAM_CHAT_ID"],
            text=ending_text,
            parse_mode='Markdown'
        )
        
        logging.info(f"Offerte inviate per la parola chiave: {keyword}")
        
    except Exception as e:
        logging.error(f"Errore generale in send_telegram_message: {e}")
