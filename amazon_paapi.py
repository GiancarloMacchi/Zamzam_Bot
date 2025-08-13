# amazon_paapi.py
import os
import json
import time
import hmac
import hashlib
import requests
from datetime import datetime
from urllib.parse import quote


class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.region = country
        self.service = "ProductAdvertisingAPI"
        self.host = f"webservices.amazon.{country}"
        self.endpoint = f"https://{self.host}/paapi5/searchitems"

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self._sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, "aws4_request")
        return k_signing

    def search_items(self, keywords, item_count=10):
        t = datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")  # Date w/o time, used in credential scope

        payload = {
            "Keywords": keywords,
            "ItemCount": item_count,
            "Resources": [
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.SavingBasis",
                "Offers.Listings.Price.Savings",
                "Images.Primary.Large",
                "DetailPageURL"
            ],
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates",
            "Marketplace": f"https://www.amazon.{self.region}"
        }

        payload_json = json.dumps(payload, separators=(",", ":"))

        # ************* TASK 1: Create a canonical request *************
        method = "POST"
        canonical_uri = "/paapi5/searchitems"
        canonical_querystring = ""

        canonical_headers = (
            f"content-encoding:\n"
            f"content-type:application/json; charset=UTF-8\n"
            f"host:{self.host}\n"
            f"x-amz-date:{amz_date}\n"
        )
        signed_headers = "content-encoding;content-type;host;x-amz-date"
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        canonical_request = (
            f"{method}\n{canonical_uri}\n{canonical_querystring}\n"
            f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
        )

        # ************* TASK 2: Create the string to sign*************
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = (
            f"{algorithm}\n{amz_date}\n{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        # ************* TASK 3: Calculate the signature *************
        signing_key = self._get_signature_key(
            self.secret_key, date_stamp, self.region, self.service
        )
        signature = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # ************* TASK 4: Add signing information to the request *************
        authorization_header = (
            f"{algorithm} Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers = {
            "Content-Encoding": "",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": self.host,
            "X-Amz-Date": amz_date,
            "Authorization": authorization_header,
        }

        # Send the request
        response = requests.post(self.endpoint, data=payload_json, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Amazon API error: {response.status_code} - {response.text}")

        data = response.json()

        class SearchResult:
            def __init__(self, data):
                self._data = data
                self.items = data.get("SearchResult", {}).get("Items", [])
            def to_dict(self):
                return self._data

        return SearchResult(data)
