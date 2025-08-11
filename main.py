import os
import logging
from utils import search_amazon_products, send_telegram_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    keywords = os.getenv("KEYWORDS", "").split(",")
    min_discount = int(os.getenv("MIN_SAVE", 20))
    amazon_country = os.getenv("AMAZON_COUNTRY", "IT").upper()

    logging.info(f"Paese Amazon: {amazon_country}")
    logging.info(f"Parole chiave: {keywords}")
    logging.info(f"Sconto minimo: {min_discount}%")

    for keyword in keywords:
        products = search_amazon_products(keyword.strip(), amazon_country, min_discount)

        for product in products:
            message = f"🔥 {product['title']}\n💰 Prezzo: {product['price']}\n💸 Sconto: {product['discount']}%\n🔗 {product['url']}"
            send_telegram_message(message)

if __name__ == "__main__":
    main()
