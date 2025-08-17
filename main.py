import logging
from config import load_config
from telegram_bot import send_telegram_message

# Esempio di feed Amazon (sostituire con la vera integrazione Amazon)
# Ogni prodotto è un dizionario con: title, url, price, image_url
example_products = [
    {
        "title": "Lego Classic 11001",
        "url": "https://www.amazon.it/dp/B000FQ9QVI",
        "price": "29,99€",
        "image_url": "https://images-na.ssl-images-amazon.com/images/I/81Z0ZrZ6D1L._AC_SL1500_.jpg"
    },
    {
        "title": "Zaino scuola bambino",
        "url": "https://www.amazon.it/dp/B07XYZ1234",
        "price": "19,90€",
        "image_url": "https://images-na.ssl-images-amazon.com/images/I/71abcd12345.jpg"
    }
]

config = load_config()
DRY_RUN = config.get("DRY_RUN", "True") == "True"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Avvio bot Amazon…")
    
    for product in example_products:
        title = product.get("title")
        url = product.get("url")
        price = product.get("price")
        image_url = product.get("image_url")

        send_telegram_message(title, url, price, image_url)

    logging.info("Esecuzione completata.")

if __name__ == "__main__":
    main()
