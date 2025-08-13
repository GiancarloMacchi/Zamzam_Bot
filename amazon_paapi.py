import requests
import json
import logging
import time
import hmac
import hashlib
import base64
from datetime import datetime
from urllib.parse import quote, urlencode
from dotenv import load_dotenv
import os

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

logger = logging.getLogger(__name__)

HOSTS = {
    "IT": "webservices.amazon.it",
    "US": "webservices.amazon.com",
    "UK": "webservices.amazon.co.uk",
    "DE": "webservices.amazon.de",
    "FR": "webservices.amazon.fr",
    "ES": "webservices.amazon.es"
}

def sign_request(params, secret_key):
    sorted_params = sorted(params.items())
    canonical_query = urlencode(sorted_params, quote_via=quote)
    string_to_sign = f"GET\n{HOSTS[AMAZON_COUNTRY]}\n/paapi5/getitems\n{canonical_query}"
    digest = hmac.new(
        bytes(secret_key, encoding="utf-8"),
        msg=bytes(string_to_sign, encoding="utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode()

def amazon_search(keywords, item_count):
    logger.info(f"🔍 Chiamata Amazon API con keyword: {keywords}")
    
    endpoint = f"https://{HOSTS[AMAZON_COUNTRY]}/paapi5/searchitems"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Host": HOSTS[AMAZON_COUNTRY],
        "X-Amz-Date": datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'),
        "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
    }
    
    payload = {
        "Keywords": keywords,
        "SearchIndex": "All",
        "ItemCount": item_count,
        "Resources": [
            "Images.Primary.Large",
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis"
        ],
        "PartnerTag": AMAZON_ASSOCIATE_TAG,
        "PartnerType": "Associates"
    }
    
    payload_json = json.dumps(payload)  # <-- FIX QUI
    
    try:
        response = requests.post(endpoint, headers=headers, data=payload_json)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"❌ Errore durante il recupero degli articoli da Amazon API:\n{e}")
        return None
