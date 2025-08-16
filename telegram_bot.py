import logging

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, text):
        """Simula l'invio di un messaggio Telegram."""
        logging.info(f"📤 [MOCK] Messaggio inviato a Telegram: {text[:60]}...")
