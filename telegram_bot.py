import logging
import telegram

def send_telegram_message(config, message: str):
    """
    Invia un messaggio al canale Telegram configurato.
    """
    try:
        bot = telegram.Bot(token=config["TELEGRAM_BOT_TOKEN"])
        bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=message, parse_mode='Markdown')
        logging.info("Messaggio inviato su Telegram")
    except Exception as e:
        logging.error(f"Errore nell'invio del messaggio Telegram: {e}")
