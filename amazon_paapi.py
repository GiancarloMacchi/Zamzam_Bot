import requests
import json
import logging
import time
from urllib.parse import quote
from hashlib import sha256
import hmac
import base64
import datetime
import os

logging.basicConfig(level=logging.INFO)

class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.country = country.lower()
        self.host = f"webservices.amazon.{self.country}"
        self.endpoint = f"https://{self.host}/paapi5/searchitems"

    def sign(self, payload):
        # Genera intestazioni firmate per Amazon PAAPI
        method = "POST"
        service = "ProductAdvertisingAPI"
        region = "eu-west-1" if self.country in ["fr", "de", "it", "es", "uk"] else "us-east-1"

        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')

        canonical_uri = "/paapi5/searchitems"
        canonical_querystring = ""
        canonical_headers = f"content-encoding:amz-1.0\ncontent-type:application/json; charset=utf-8\nhost:{self.host}\nx-amz-date:{amz_date}\n"
        signed_headers = "content-encoding;content-type;host;x-amz-date"

        payload_hash = sha256(payload.encode('utf-8')).hexdigest()

        canonical_request = '\n'.join([method, canonical_uri, canonical_querystring,
                                       canonical_headers, signed_headers, payload_hash])

        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f"{datestamp}/{region}/{service}/aws4_request"
        string_to_sign = '\n'.join([algorithm, amz_date, credential_scope,
                                    sha256(canonical_request.encode('utf-8')).hexdigest()])

        def sign_key(key, msg):
            return hmac.new(key, msg.encode('utf-8'), sha256).digest()

        k_date = sign_key(('AWS4' + self.secret_key).encode('utf-8'), datestamp)
        k_region = sign_key(k_date, region)
        k_service = sign_key(k_region, service)
        k_signing = sign_key(k_service, 'aws4_request')

        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), sha256).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers = {
            'Content-Encoding': 'amz-1.0',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': self.host,
            'X-Amz-Date': amz_date,
            'Authorization': authorization_header
        }

        return headers

    def search_items(self, keywords, item_count=10, min_saving_percent=0):
        payload = json.dumps({
            "Keywords": keywords,
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates",
            "Marketplace": f"www.amazon.{self.country}",
            "ItemCount": item_count,
            "Resources": [
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis"
            ]
        })

        headers = self.sign(payload)
        try:
            response = requests.post(self.endpoint, data=payload, headers=headers)
            if response.status_code != 200:
                logging.error(f"Amazon API error: {response.status_code} - {response.text}")
                return []
            data = response.json()
            if "SearchResult" not in data or "Items" not in data["SearchResult"]:
                return []
            return data["SearchResult"]["Items"]
        except Exception as e:
            logging.error(f"Errore nella richiesta Amazon API: {e}")
            return []
