import logging
from telegram import Bot


def send_telegram_message(config, message: str):
    """
    Invia un messaggio al canale Telegram configurato.
    Usa il bot token e chat id definiti nelle variabili di ambiente / config.
    """
    try:
        bot = Bot(token=config["TELEGRAM_BOT_TOKEN"])
        bot.send_message(chat_id=config["TELEGRAM_CHAT_ID"], text=message)
        logging.info("Messaggio inviato su Telegram")
    except Exception as e:
        logging.error(f"Errore nell'invio del messaggio Telegram: {e}")
