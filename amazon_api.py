import os
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models import GetItemsRequest, SearchItemsRequest
from paapi5_python_sdk.paapi5_python_sdk import Paapi5PythonSdk
from paapi5_python_sdk.configuration import Configuration
from paapi5_python_sdk.api_client import ApiClient

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT").lower()

def get_amazon_client():
    """
    Restituisce un'istanza dell'API client ufficiale Amazon PAAPI.
    """
    if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG]):
        raise ValueError("Chiavi di accesso Amazon e Associate Tag devono essere impostati nei secrets.")

    host = f"webservices.amazon.{AMAZON_COUNTRY}"
    config = Configuration(
        access_key=AMAZON_ACCESS_KEY,
        secret_key=AMAZON_SECRET_KEY,
        host=host
    )
    api_client = ApiClient(configuration=config)
    return DefaultApi(api_client)
