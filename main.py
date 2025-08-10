# main.py
import os
from amazon_api import get_amazon_products
import requests

# Funzione aggiornata per accettare token, chat_id e message
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(f"Errore Telegram API: {response.status_code} - {response.text}")

def check_env_variables():
    required_vars = [
        "AMAZON_ACCESS_KEY",
        "AMAZON_SECRET_KEY",
        "AMAZON_ASSOCIATE_TAG",
        "AMAZON_COUNTRY",
        "BITLY_TOKEN",
        "ITEM_COUNT",
        "KEYWORDS",
        "MIN_SAVE",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Mancano le seguenti variabili d'ambiente: {', '.join(missing_vars)}")
        exit(1)
    else:
        print("✅ Tutte le variabili d'ambiente sono presenti.")

def main():
    check_env_variables()
    
    keywords = os.getenv("KEYWORDS")
    amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
    amazon_secret_key = os.getenv("AMAZON_SECRET_KEY")
    amazon_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
    
    try:
        products = get_amazon_products(keywords, amazon_access_key, amazon_secret_key, amazon_tag)
        
        if not products:
            message = "Nessun prodotto trovato."
        else:
            message = "Prodotti trovati:\n" + "\n".join([p["ItemInfo"]["Title"]["DisplayValue"] for p in products])
        
        send_telegram_message(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"), message)
    
    except Exception as e:
        send_telegram_message(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"), f"Errore: {e}")

if __name__ == "__main__":
    main()
