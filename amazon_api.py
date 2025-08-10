import requests
import datetime
import hashlib
import hmac
import base64
from urllib.parse import quote

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing

def get_amazon_products(keyword, amazon_access_key, amazon_secret_key, amazon_partner_tag, region="us-east-1", marketplace="www.amazon.com"):
    """
    Cerca prodotti su Amazon usando PA-API 5.0
    """
    # Endpoint
    endpoint = f"https://webservices.amazon.com/paapi5/searchitems"
    host = "webservices.amazon.com"
    service = "ProductAdvertisingAPI"
    content_type = "application/json; charset=UTF-8"

    # Data
    now = datetime.datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')

    # Corpo della richiesta
    payload = {
        "Keywords": keyword,
        "SearchIndex": "All",
        "PartnerTag": amazon_partner_tag,
        "PartnerType": "Associates",
        "Resources": [
            "ItemInfo.Title",
            "Offers.Listings.Price"
        ]
    }

    import json
    request_payload = json.dumps(payload)

    # Step 1: Creazione della richiesta canonica
    canonical_uri = "/paapi5/searchitems"
    canonical_querystring = ""
    canonical_headers = f"content-type:{content_type}\nhost:{host}\nx-amz-date:{amz_date}\n"
    signed_headers = "content-type;host;x-amz-date"
    payload_hash = hashlib.sha256(request_payload.encode('utf-8')).hexdigest()
    canonical_request = f"POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

    # Step 2: Creazione della stringa da firmare
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    # Step 3: Firma
    signing_key = get_signature_key(amazon_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # Step 4: Autorizzazione
    authorization_header = (
        f"{algorithm} Credential={amazon_access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    # Step 5: Headers finali
    headers = {
        "Content-Type": content_type,
        "X-Amz-Date": amz_date,
        "Authorization": authorization_header
    }

    # Richiesta
    response = requests.post(endpoint, headers=headers, data=request_payload)

    if response.status_code != 200:
        raise Exception(f"Amazon API error: {response.status_code} - {response.text}")

    return response.json()
