import os
from amazon_paapi import AmazonApi
from telegram import Bot

# --- Lettura variabili dai Secrets ---
access_key = os.environ.get("AMAZON_ACCESS_KEY")
secret_key = os.environ.get("AMAZON_SECRET_KEY")
partner_tag = os.environ.get("AMAZON_ASSOCIATE_TAG")
region = os.environ.get("AMAZON_COUNTRY", "IT")
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

# --- Controllo variabili ---
if not all([access_key, secret_key, partner_tag, telegram_token, telegram_chat_id]):
    raise ValueError("⚠️ Mancano una o più variabili nei Secrets di GitHub!")

# --- Inizializzo Amazon API ---
amazon = AmazonApi(access_key, secret_key, partner_tag, region)

# --- Inizializzo Telegram Bot ---
bot = Bot(token=telegram_token)

def main():
    try:
        # 🔍 Ricerca prodotti (puoi cambiare le keywords)
        products = amazon.search_products(keywords="laptop", search_index="All", item_count=3)

        if not products:
            bot.send_message(chat_id=telegram_chat_id, text="Nessun prodotto trovato.")
            return

        # 📩 Invio risultati su Telegram
        for product in products:
            message = f"📦 {product.title}\n💰 Prezzo: {product.list_price}\n🔗 {product.detail_page_url}"
            bot.send_message(chat_id=telegram_chat_id, text=message)

    except Exception as e:
        error_message = f"Errore durante la ricerca o invio: {e}"
        print(error_message)
        bot.send_message(chat_id=telegram_chat_id, text=error_message)

if __name__ == "__main__":
    main()
