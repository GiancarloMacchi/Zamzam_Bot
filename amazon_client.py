import os
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models import (
    GetItemsRequest, GetItemsResource,
    PartnerType
)
from paapi5_python_sdk.rest import ApiException
from paapi5_python_sdk import configuration

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

config = configuration.Configuration(
    access_key=AMAZON_ACCESS_KEY,
    secret_key=AMAZON_SECRET_KEY,
    host=f"webservices.amazon.{AMAZON_COUNTRY.lower()}",
    region="eu-west-1"
)

api_client = DefaultApi(api_client=None, configuration=config)

def get_items(item_ids):
    try:
        resources = [
            GetItemsResource.ITEMINFO_TITLE,
            GetItemsResource.OFFERS_LISTINGS_PRICE
        ]
        request = GetItemsRequest(
            partner_tag=AMAZON_ASSOCIATE_TAG,
            partner_type=PartnerType.ASSOCIATES,
            marketplace=f"A1PA6795UKMFR9",  # codice marketplace Amazon IT
            item_ids=item_ids,
            resources=resources
        )
        response = api_client.get_items(request)
        return response
    except ApiException as e:
        print(f"Errore Amazon API: {e}")
        return None
