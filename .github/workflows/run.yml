from amightygirl.paapi5_python_sdk import AmazonApi
import os

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

def get_amazon_client():
    """
    Crea e restituisce un'istanza del client Amazon PAAPI.
    """
    if not all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG]):
        raise ValueError("Le chiavi di accesso e l'associate tag di Amazon devono essere impostati.")

    return AmazonApi(
        access_key=AMAZON_ACCESS_KEY,
        secret_key=AMAZON_SECRET_KEY,
        partner_tag=AMAZON_ASSOCIATE_TAG,
        host=f"webservices.amazon.{AMAZON_COUNTRY.lower()}"
    )
