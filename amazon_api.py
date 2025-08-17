import hashlib
import hmac
import base64
import requests
from datetime import datetime
from urllib.parse import quote, urlencode
from config import load_config

config = load_config()

AMAZON_ACCESS_KEY = config["AMAZON_ACCESS_KEY"]
AMAZON_SECRET_KEY = config["AMAZON_SECRET_KEY"]
AMAZON_ASSOCIATE_TAG = config["AMAZON_ASSOCIATE_TAG"]
AMAZON_COUNTRY = config["AMAZON_COUNTRY"]
ITEM_COUNT = int(config["ITEM_COUNT"])

ENDPOINTS = {
    "it": "webservices.amazon.it",
    "com": "webservices.amazon.com",
    "uk": "webservices.amazon.co.uk"
}

def sign_request(params, endpoint):
    """
    Firma la richiesta per Amazon PA-API.
    """
    params["Timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sorted_params = sorted(params.items())
    canonical_query_string = urlencode(sorted_params, quote_via=quote)
    string_to_sign = f"GET\n{endpoint}\n/onca/xml\n{canonical_query_string}"
    signature = base64.b64encode(hmac.new(
        AMAZON_SECRET_KEY.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).digest()).decode()
    return canonical_query_string + "&Signature=" + quote(signature)

def search_amazon(keyword):
    """
    Cerca prodotti reali su Amazon via PA-API.
    Restituisce lista di dizionari: title, url, price, image_url
    """
    endpoint = ENDPOINTS.get(AMAZON_COUNTRY, "webservices.amazon.it")
    params = {
        "Service": "AWSECommerceService",
        "Operation": "ItemSearch",
        "AWSAccessKeyId": AMAZON_ACCESS_KEY,
        "AssociateTag": AMAZON_ASSOCIATE_TAG,
        "SearchIndex": "All",
        "Keywords": keyword,
        "ResponseGroup": "Images,ItemAttributes,Offers",
        "ItemPage": "1"
    }

    signed_url = f"https://{endpoint}/onca/xml?{sign_request(params, endpoint)}"
    response = requests.get(signed_url)

    products = []
    if response.status_code == 200:
        # parsing XML base (puoi usare xml.etree.ElementTree o altro)
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(response.content)
        for item in tree.findall(".//Item")[:ITEM_COUNT]:
            title = item.findtext(".//Title")
            url = item.findtext(".//DetailPageURL")
            price = item.findtext(".//FormattedPrice")
            image_url = item.findtext(".//MediumImage/URL")
            products.append({
                "title": title or "N/D",
                "url": url or "#",
                "price": price or "N/D",
                "image_url": image_url or None
            })
    else:
        print(f"Errore API Amazon: {response.status_code}")
    return products
