import os
import random
import logging
from dotenv import load_dotenv
from amazon_paapi import AmazonApi
from telegram import Bot

# Carica variabili ambiente
load_dotenv()

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Credenziali Amazon
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

# Credenziali Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Parametri di ricerca
KEYWORDS = os.getenv("KEYWORDS", "infanzia,mamma,bimbo,bambino,bambina").split(",")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 5))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))

# Frasi spiritose
MESSAGGI_DIVERTENTI = [
    "✨ Offerta imperdibile!",
    "🚀 Affrettati, prima che sparisca!",
    "🎯 Colpo di fortuna trovato!",
    "🔥 Sconto pazzesco!",
    "🎁 Non lasciartelo scappare!",
    "🛒 Aggiungilo subito al carrello!",
]

# Whitelist di categorie consentite
CATEGORIE_CONSENTITE = [
    "bambini", "neonati", "infanzia", "mamma", "bimbo", "bambino", "bambina",
    "ragazzo", "ragazza", "adolescente", "scuola", "asilo", "giochi", "giocattoli",
    "premaman", "libri", "abbigliamento", "scarpe", "zaini", "cancelleria"
]

def prodotto_consentito(categorie_prodotto):
    if not categorie_prodotto:
        return False, "Nessuna categoria disponibile"
    categorie_prodotto_lower = [c.lower() for c in categorie_prodotto]
    for cat in categorie_prodotto_lower:
        for consentita in CATEGORIE_CONSENTITE:
            if consentita in cat:
                return True, f"Categoria consentita: {cat}"
    return False, f"Nessuna categoria valida trovata ({categorie_prodotto_lower})"

def main():
    logging.info(f"🚀 Avvio bot Amazon - Partner tag: {AMAZON_ASSOCIATE_TAG}")
    amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    for keyword in KEYWORDS:
        logging.info(f"🔍 Ricerca per: {keyword}")
        try:
            results = amazon.search_items(
                keyword,
                item_count=ITEM_COUNT,
                resources=["Images.Primary.Large", "ItemInfo.Title", "Offers.Listings.Price", 
                           "Offers.Listings.SavingBasis", "ItemInfo.Classifications"]
            )

            if not results.items:
                logging.warning(f"[NESSUN RISULTATO] per '{keyword}'")
                continue

            for item in results.items:
                title = item.item_info.title.display_value if item.item_info.title else "Senza titolo"
                url = item.detail_page_url
                image_url = item.images.primary.large.url if item.images and item.images.primary and item.images.primary.large else None

                # Prezzo e sconto
                try:
                    price = item.offers.listings[0].price.amount
                    saving_basis = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else price
                    save_percent = int((saving_basis - price) / saving_basis * 100)
                except Exception:
                    logging.info(f"[SCARTATO] '{title}' → Prezzo non disponibile")
                    continue

                # Controllo sconto minimo
                if save_percent < MIN_SAVE:
                    logging.info(f"[SCARTATO] '{title}' → Sconto {save_percent}% inferiore al minimo {MIN_SAVE}%")
                    continue

                # Controllo categorie
                categorie = []
                if item.item_info.classifications:
                    if item.item_info.classifications.product_group:
                        categorie.append(item.item_info.classifications.product_group.display_value)
                    if item.item_info.classifications.binding:
                        categorie.append(item.item_info.classifications.binding.display_value)

                consentito, motivo = prodotto_consentito(categorie)
                if not consentito:
                    logging.info(f"[SCARTATO] '{title}' → {motivo}")
                    continue
                else:
                    logging.info(f"[OK] '{title}' → {motivo}")

                # Messaggio Telegram
                messaggio = f"{random.choice(MESSAGGI_DIVERTENTI)}\n\n" \
                            f"{title}\n" \
                            f"💰 Prezzo: {price}€ (-{save_percent}%)\n" \
                            f"🔗 {url}"

                if image_url:
                    bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image_url, caption=messaggio)
                else:
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio)

        except Exception as e:
            logging.error(f"[ERRORE Amazon] ricerca '{keyword}': {e}")

    logging.info("✅ Bot completato")

if __name__ == "__main__":
    main()
