import os
import logging
from amazon_paapi_sdk import AmazonApi
from amazon_paapi_sdk.models.search_items_request import SearchItemsRequest
from amazon_paapi_sdk.models.search_items_resource import SearchItemsResource

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="***%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)

# Variabili ambiente
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

# Risorse richieste (solo qui, per evitare doppioni)
RESOURCES = [
    SearchItemsResource.ITEMINFO_TITLE,
    SearchItemsResource.OFFERS_LISTINGS_PRICE,
    SearchItemsResource.OFFERS_LISTINGS_SAVINGBASIS,
    SearchItemsResource.IMAGES_PRIMARY_LARGE
]

# Inizializza API Amazon
amazon = AmazonApi(
    access_key=AMAZON_ACCESS_KEY,
    secret_key=AMAZON_SECRET_KEY,
    partner_tag=AMAZON_ASSOCIATE_TAG,
    host=f"webservices.amazon.{AMAZON_COUNTRY}",
    region="eu-west-1"
)

failed_keywords = 0

# Ciclo sulle keyword
for keyword in KEYWORDS:
    keyword = keyword.strip()
    if not keyword:
        continue

    logging.info(f"🔍 Cerco: {keyword}")

    try:
        request = SearchItemsRequest(
            Keywords=keyword,
            SearchIndex="All",
            Resources=RESOURCES
        )

        response = amazon.search_items(request)

        if not response.search_result or not response.search_result.items:
            logging.warning(f"❌ Nessun risultato per '{keyword}'")
            failed_keywords += 1
            continue

        for item in response.search_result.items:
            title = item.item_info.title.display_value if item.item_info and item.item_info.title else "Senza titolo"
            logging.info(f"✅ {title}")

    except Exception as e:
        logging.error(f"Errore ricerca '{keyword}': {e}")
        failed_keywords += 1

logging.info(f"📊 Keyword fallite: {failed_keywords}")
