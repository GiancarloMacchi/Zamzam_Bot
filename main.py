import os
import logging
from datetime import datetime
from utils import get_amazon_client, shorten_url, filter_products
from telegram import Bot

# Nome file log con data e ora
log_filename = f"bot_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def main():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    keywords = os.getenv("KEYWORDS", "infanzia,bambini,scuola").split(",")

    amazon = get_amazon_client()

    for keyword in keywords:
        try:
            logging.info(f"🔍 Ricerca Amazon per keyword: {keyword}")
            items = amazon.search_items(
                keywords=keyword,
                item_count=int(os.getenv("ITEM_COUNT", 10)),
                resources=[
                    "Images.Primary.Large",
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis.Price",
                    "Offers.Listings.Savings",
                    "ItemInfo.ProductInfo"
                ]
            )

            filtered_items = filter_products(items)
            logging.info(f"✅ Prodotti filtrati per '{keyword}': {len(filtered_items)}")

            for item in filtered_items:
                try:
                    title = item.item_info.title.display_value
                    url = shorten_url(item.detail_page_url)
                    discount = item.offers.listings[0].price.savings.percentage
                    message = f"🎯 {title}\n💰 Sconto: {discount}%\n🔗 {url}"
                    bot.send_message(chat_id=chat_id, text=message)
                    logging.info(f"📤 Inviato: {title} ({discount}%)")
                except Exception as e:
                    logging.error(f"Errore nell'invio di un prodotto: {e}")
                    continue

        except Exception as e:
            logging.error(f"Errore nella ricerca con keyword '{keyword}': {e}")
            continue

if __name__ == "__main__":
    main()
