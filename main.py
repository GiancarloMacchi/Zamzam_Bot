import os
import json
import random
from datetime import datetime
from telegram_api import send_telegram_message
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models import GetItemsRequest, PartnerType
from paapi5_python_sdk.rest import ApiException
import paapi5_python_sdk

# Carica frasi
with open("phrases.json", "r", encoding="utf-8") as f:
    phrases = json.load(f)

# Imposta credenziali Amazon PA-API
access_key = os.getenv("AMAZON_ACCESS_KEY")
secret_key = os.getenv("AMAZON_SECRET_KEY")
partner_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
region = os.getenv("AMAZON_COUNTRY", "IT")

# Lista ASIN di esempio (poi potrai metterli da un file o query dinamiche)
asin_list = ["B0036QXU48", "B0D1234567"]

# Funzione per selezionare frase
def get_random_phrase(category):
    if category in phrases:
        return random.choice(phrases[category])
    else:
        return random.choice(phrases["default"])

# Configura client Amazon
def get_amazon_client():
    config = paapi5_python_sdk.Configuration(
        access_key=access_key,
        secret_key=secret_key,
        host=f"webservices.amazon.{region.lower()}",
        region=region.upper()
    )
    return DefaultApi(paapi5_python_sdk.ApiClient(config))

# Recupera prodotti da Amazon
def fetch_amazon_items(asin_list):
    api_client = get_amazon_client()
    request = GetItemsRequest(
        partner_tag=partner_tag,
        partner_type=PartnerType.ASSOCIATES,
        marketplace=f"www.amazon.{region.lower()}",
        item_ids=asin_list,
        resources=[
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
        ]
    )
    try:
        response = api_client.get_items(request)
        return response.items_result.items
    except ApiException as e:
        print("Errore API Amazon:", e)
        return []

# Invia messaggi
def main():
    items = fetch_amazon_items(asin_list)
    for item in items:
        title = item.item_info.title.display_value
        price = item.offers.listings[0].price.display_amount if item.offers else "N/A"
        url = item.detail_page_url
        image = item.images.primary.medium.url if item.images else None

        phrase = get_random_phrase("infanzia")  # categoria esempio

        message = f"{phrase}\n📦 <b>{title}</b>\n💰 {price}\n🔗 {url}"
        send_telegram_message(message, image)

if __name__ == "__main__":
    main()
