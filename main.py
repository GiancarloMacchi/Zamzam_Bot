import os
from utils import search_amazon_products, send_telegram_message

MIN_DISCOUNT = int(os.getenv("MIN_SAVE", 20))

CATEGORIES = [
    "prodotti per bambini",
    "giocattoli",
    "articoli per la scuola",
    "accessori per neonati",
    "libri per bambini",
    "abbigliamento bambini",
    "articoli per genitori",
    "seggiolini auto",
    "passeggini",
    "giochi educativi"
]

def main():
    for category in CATEGORIES:
        try:
            products = search_amazon_products(category)
        except Exception as e:
            print(f"Errore nella ricerca per '{category}': {e}")
            continue

        for product in products:
            try:
                if not product.get("Offers"):
                    continue

                offer = product["Offers"][0]
                price = offer["Price"]["Amount"]
                list_price = offer["Price"]["ListPrice"]["Amount"]
                discount = round((list_price - price) / list_price * 100, 2)

                if discount >= MIN_DISCOUNT:
                    message = (
                        f"📦 {product['ItemInfo']['Title']['DisplayValue']}\n"
                        f"💰 Prezzo: {price}€ (Sconto {discount}%)\n"
                        f"🔗 {product['DetailPageURL']}"
                    )
                    send_telegram_message(message)

            except Exception as e:
                print(f"Errore nel processare un prodotto: {e}")
                continue

if __name__ == "__main__":
    main()
