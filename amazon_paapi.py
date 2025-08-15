# amazon_paapi.py
import requests
import datetime
import hashlib
import hmac
import json
import logging
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class AmazonAPI:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.country = country.lower()
        self.host = f"webservices.amazon.{self._get_tld()}"
        self.endpoint = f"https://{self.host}/paapi5/searchitems"

    def _get_tld(self):
        tlds = {
            "it": "it",
            "us": "com",
            "uk": "co.uk",
            "de": "de",
            "fr": "fr",
            "es": "es"
        }
        return tlds.get(self.country, "com")

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, date_stamp, region):
        kDate = self._sign(('AWS4' + self.secret_key).encode('utf-8'), date_stamp)
        kRegion = self._sign(kDate, region)
        kService = self._sign(kRegion, 'ProductAdvertisingAPI')
        kSigning = self._sign(kService, 'aws4_request')
        return kSigning

    def search_items(self, keywords, resources=None, item_count=10):
        if resources is None:
            resources = [
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price"
            ]

        payload = {
            "Keywords": keywords,
            "Resources": resources,
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates",
            "Marketplace": f"www.amazon.{self._get_tld()}",
            "ItemCount": item_count
        }

        # AWS Signing parameters
        method = "POST"
        service = "ProductAdvertisingAPI"
        region = self.country
        content_type = "application/json; charset=UTF-8"
        amz_target = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"

        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')

        canonical_uri = "/paapi5/searchitems"
        canonical_querystring = ""
        canonical_headers = f"content-encoding:amz-1.0\nhost:{self.host}\nx-amz-date:{amz_date}\nx-amz-target:{amz_target}\n"
        signed_headers = "content-encoding;host;x-amz-date;x-amz-target"
        payload_json = json.dumps(payload)
        payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()

        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        signing_key = self._get_signature_key(date_stamp, region)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers = {
            "Content-Encoding": "amz-1.0",
            "Content-Type": content_type,
            "X-Amz-Date": amz_date,
            "X-Amz-Target": amz_target,
            "Authorization": authorization_header
        }

        try:
            response = requests.post(self.endpoint, data=payload_json, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("SearchResult", {}).get("Items", [])
        except Exception as e:
            logger.error(f"❌ Errore chiamata Amazon API: {e}")
            return []
