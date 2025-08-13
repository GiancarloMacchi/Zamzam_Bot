# amazon_paapi.py
import os
import json
import time
import hmac
import hashlib
import base64
import requests
from urllib.parse import quote, urlencode
from collections import namedtuple

class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.endpoint = f"webservices.amazon.{country}"
        self.host = f"https://{self.endpoint}/paapi5/searchitems"

    def _sign(self, payload):
        # Firma HMAC richiesta da Amazon
        return base64.b64encode(
            hmac.new(
                self.secret_key.encode("utf-8"),
                payload.encode("utf-8"),
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

    def search_items(self, keywords, item_count=10):
        payload = {
            "Keywords": keywords,
            "ItemCount": item_count,
            "Resources": [
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.SavingBasis.Amount",
                "Offers.Listings.SavingBasis.Currency",
                "Offers.Listings.Price.Savings",
                "Images.Primary.Large",
                "DetailPageURL"
            ],
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates",
            "Marketplace": f"www.amazon.{self.endpoint.split('.')[-1]}"
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Host": self.endpoint,
            "X-Amz-Date": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
            "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
            "X-Amz-AccessKeyId": self.access_key,
        }

        # Firma AWS V4
        signed_headers = self._sign(json.dumps(payload))
        headers["X-Amz-Signature"] = signed_headers

        resp = requests.post(self.host, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"Amazon API error: {resp.status_code} - {resp.text}")

        data = resp.json()

        # Creiamo oggetto compatibile
        class SearchResult:
            def __init__(self, data):
                self._data = data
                self.items = data.get("SearchResult", {}).get("Items", [])
            def to_dict(self):
                return self._data

        return SearchResult(data)
