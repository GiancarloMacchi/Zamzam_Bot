# amazon_api.py
import requests
import datetime
import hashlib
import hmac
import json

def get_amazon_products(
    keywords,
    amazon_access_key,
    amazon_secret_key,
    amazon_tag,
    region="eu-west-1",
    host="webservices.amazon.it"
):
    """
    Recupera prodotti da Amazon PA API 5.0
    """
    endpoint = f"https://{host}/paapi5/searchitems"
    payload = {
        "Keywords": keywords,
        "PartnerTag": amazon_tag,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.it",
        "Resources": [
            "Images.Primary.Medium",
            "ItemInfo.Title",
            "Offers.Listings.Price"
        ]
    }

    # Timestamp e firma richiesta
    t = datetime.datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    canonical_uri = "/paapi5/searchitems"
    canonical_querystring = ""
    canonical_headers = f"content-encoding:amz-1.0\nhost:{host}\nx-amz-date:{amz_date}\n"
    signed_headers = "content-encoding;host;x-amz-date"
    payload_json = json.dumps(payload)

    canonical_request = f"POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashlib.sha256(payload_json.encode('utf-8')).hexdigest()}"
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{region}/ProductAdvertisingAPI/aws4_request"

    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(key, dateStamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning

    signing_key = getSignatureKey(amazon_secret_key, date_stamp, region, "ProductAdvertisingAPI")
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        "Content-Encoding": "amz-1.0",
        "Content-Type": "application/json; charset=utf-8",
        "Host": host,
        "X-Amz-Date": amz_date,
        "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
        "Authorization": f"{algorithm} Credential={amazon_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    }

    response = requests.post(endpoint, headers=headers, data=payload_json)

    if response.status_code != 200:
        raise Exception(f"Amazon API error: {response.status_code}, {response.text}")

    data = response.json()
    return data.get("SearchResult", {}).get("Items", [])
