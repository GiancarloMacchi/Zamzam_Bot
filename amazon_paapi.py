# amazon_paapi.py
import os
import sys
import json
import time
import hmac
import hashlib
import requests
import logging
from datetime import datetime
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class AmazonAPI:
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.country = os.getenv("AMAZON_COUNTRY", "it").lower()
        self.region = "eu-west-1" if self.country in ["it", "fr", "de", "es", "uk"] else "us-east-1"
        self.service = "ProductAdvertisingAPI"
        self.endpoint = f"https://webservices.amazon.{self._get_tld()}/paapi5/searchitems"

        if not all([self.access_key, self.secret_key, self.associate_tag]):
            logger.error("❌ Mancano le credenziali Amazon nelle secrets!")
            sys.exit(1)

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
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self._sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, "aws4_request")
        return k_signing

    def search_items(self, keywords, item_count=10):
        logger.info(f"🔍 Chiamata Amazon API con keyword: {keywords}")

        # Corpo della richiesta
        payload = {
            "Keywords": keywords,
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates",
            "SearchIndex": "All",
            "ItemCount": item_count,
            "Resources": [
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "DetailPageURL"
            ]
        }
        request_payload = json.dumps(payload)

        # Preparazione firma
        t = datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        canonical_uri = "/paapi5/searchitems"
        canonical_querystring = ""
        canonical_headers = f"content-encoding:amz-1.0\ncontent-type:application/json; charset=utf-8\nhost:webservices.amazon.{self._get_tld()}\nx-amz-date:{amz_date}\n"
        signed_headers = "content-encoding;content-type;host;x-amz-date"
        payload_hash = hashlib.sha256(request_payload.encode("utf-8")).hexdigest()
        canonical_request = f"POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        signing_key = self._get_signature_key(self.secret_key, date_stamp, self.region, self.service)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        headers = {
            "Content-Encoding": "amz-1.0",
            "Content-Type": "application/json; charset=utf-8",
            "Host": f"webservices.amazon.{self._get_tld()}",
            "X-Amz-Date": amz_date,
            "Authorization": f"{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        }

        try:
            r = requests.post(self.endpoint, data=request_payload, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            logger.debug(f"📨 Risposta completa Amazon: {json.dumps(data, indent=2)}")

            # Controllo errori nella risposta
            if "Errors" in data:
                logger.error(f"⚠️ Errore Amazon API: {data['Errors']}")
                return []

            return data.get("SearchResult", {}).get("Items", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Errore nella richiesta Amazon: {e}")
            return []
