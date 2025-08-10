import os
import logging
from utils import search_amazon_products, send_telegram_message

logging.basicConfig(level=logging.INFO)

MIN_DISCOUNT = int(os.getenv("MIN_SAVE", 20))

def main():
    try:
        logging.info("Avvio ricerca prodotti Amazon...")

        products = search_amazon_products()
        logging.info(f"Trovati {len(products)} prodotti totali.")

        sent_count = 0
        for product in products:
            try:
                # Salta se non ha offerte
                if "Offers" not in product or not product["Offers"]:
                    continue

                offer = product["Offers"][0]
                price = float(offer.get("Price", 0))
                list_price = float(offer.get("ListPrice", 0))

                if list_price <= 0:
                    continue

                discount_percentage = int(((list_price - price) / list_price) * 100)

                # Filtri: sconto minimo e categorie infanzia/scuola
                categories = [c.lower() for c in product.get("Categories", [])]
                infanzia_keywords = ["bambini", "neonati", "infanzia", "scuola", "maternità", "giocattoli"]
                if discount_percentage < MIN_DISCOUNT or not any(k in " ".join(categories) for k in infanzia_keywords):
                    continue

                # Filtro lingua italiana
                title = product.get("Title", "").lower()
                if not any(parola in title for parola in ["il", "la", "un", "una", "per", "con", "bambino", "bambina"]):
                    continue

                # Prepara messaggio
                message = f"📦 {product.get('Title', 'Senza titolo')}\n"
                message += f"💰 Prezzo: {price}€\n"
                message += f"🔻 Sconto: {discount_percentage}%\n"
                message += f"🔗 {product.get('ShortUrl', product.get('Url', ''))}"

                send_telegram_message(message, image_url=product.get("Image"))

                sent_count += 1

            except Exception as e:
                logging.error(f"Errore su un prodotto: {e}")
                continue

        logging.info(f"Invio completato: {sent_count} prodotti inviati.")

    except Exception as e:
        logging.error(f"Errore generale: {e}")

if __name__ == "__main__":
    main()
