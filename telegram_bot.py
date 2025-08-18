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
        
        # Testo di introduzione personalizzato
        intro_text = f"🥳 Ciao amici! René e i suoi amici hanno scoperto delle offerte super divertenti su Amazon!\n\n"
        message_chunks = []

        # Formattazione per ogni prodotto con l'immagine
        for p in products_list:
            # Crea un singolo messaggio per ogni prodotto per l'immagine
            product_message = ""
            product_message += f"**🤩 {p['title']}**\n"
            product_message += f"Sconto: {p['discount']}% 🔥\n"
            product_message += f"Prezzo: {p['price']}€\n"
            product_message += f"Link: {p['url']}\n\n"
            
            # Invia il messaggio con l'immagine allegata
            await bot.send_photo(
                chat_id=config["TELEGRAM_CHAT_ID"],
                photo=p['image'],
                caption=product_message,
                parse_mode='Markdown'
            )
            time.sleep(2) # Breve pausa tra un post e l'altro

        # Messaggio di conclusione (opzionale, lo puoi unire al primo)
        ending_text = "✨ C'è una soluzione per ogni problema, e un gioco per ogni sorriso! Trova il tuo preferito per divertirti con René! ✨"
        await bot.send_message(
            chat_id=config["TELEGRAM_CHAT_ID"],
            text=ending_text,
            parse_mode='Markdown'
        )
        
        logging.info(f"Offerte inviate per la parola chiave: {keyword}")
        
    except Exception as e:
        logging.error(f"Errore durante l'invio del messaggio Telegram: {e}")
