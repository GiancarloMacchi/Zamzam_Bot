import requests
import datetime
import hashlib
import hmac
import logging
import os

class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.host = f"webservices.amazon.{country}"
        self.region = "eu-west-1"
        self.service = "ProductAdvertisingAPI"
        self.endpoint = f"https://{self.host}/paapi5/searchitems"

    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self.sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = self.sign(k_date, region_name)
        k_service = self.sign(k_region, service_name)
        k_signing = self.sign(k_service, "aws4_request")
        return k_signing

    def search_items(self, keywords, item_count, resources):
        logging.info(f"🔍 Chiamata Amazon API con keyword: {keywords}")

        payload = {
            "Keywords": keywords,
            "ItemCount": item_count,
            "Resources": resources,
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates",
            "Marketplace": f"www.amazon.{self.host.split('.')[-1]}"
        }

        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        canonical_uri = "/paapi5/searchitems"
        canonical_querystring = ""
        canonical_headers = f"content-encoding:amz-1.0\nhost:{self.host}\nx-amz-date:{amz_date}\n"
        signed_headers = "content-encoding;host;x-amz-date"
        payload_json = requests.utils.json.dumps(payload)
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        canonical_request = (
            f"POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = (
            f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        signing_key = self.get_signature_key(self.secret_key, date_stamp, self.region, self.service)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        headers = {
            "Content-Encoding": "amz-1.0",
            "Content-Type": "application/json; charset=utf-8",
            "Host": self.host,
            "X-Amz-Date": amz_date,
            "Authorization": f"{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        }

        response = requests.post(self.endpoint, headers=headers, data=payload_json)
        response.raise_for_status()
        return response.json()
