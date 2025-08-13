import logging
import requests
import datetime
import hashlib
import hmac
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.country = country.lower()
        self.endpoint = f"webservices.amazon.{self._domain_for_country()}"

    def _domain_for_country(self):
        domains = {
            "us": "com", "it": "it", "de": "de", "fr": "fr",
            "es": "es", "uk": "co.uk", "ca": "ca", "jp": "co.jp"
        }
        return domains.get(self.country, "com")

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self._sign(('AWS4' + key).encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, 'aws4_request')
        return k_signing

    def search_items(self, keywords):
        host = self.endpoint
        region = self.country if self.country != "uk" else "eu-west-1"
        if self.country in ["it", "fr", "es", "de", "uk"]:
            region = "eu-west-1"

        service = 'ProductAdvertisingAPI'
        amz_target = 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems'
        content_type = 'application/json; charset=UTF-8'

        request_payload = {
            "Keywords": keywords,
            "SearchIndex": "All",
            "Resources": [
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "Offers.Listings.Price"
            ],
            "PartnerTag": self.associate_tag,
            "PartnerType": "Associates"
        }

        import json
        request_payload_str = json.dumps(request_payload)

        # Date stamps
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')

        # ************* TASK 1: Create canonical request *************
        method = 'POST'
        canonical_uri = '/paapi5/searchitems'
        canonical_querystring = ''
        canonical_headers = f'content-encoding:\nhost:{host}\nx-amz-date:{amz_date}\nx-amz-target:{amz_target}\n'
        signed_headers = 'content-encoding;host;x-amz-date;x-amz-target'
        payload_hash = hashlib.sha256(request_payload_str.encode('utf-8')).hexdigest()
        canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

        # ************* TASK 2: Create the string to sign*************
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
        string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'

        # ************* TASK 3: Calculate the signature *************
        signing_key = self._get_signature_key(self.secret_key, date_stamp, region, service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # ************* TASK 4: Add signing information to the request *************
        endpoint_url = f'https://{host}/paapi5/searchitems'
        headers = {
            'Content-Encoding': '',
            'Content-Type': content_type,
            'Host': host,
            'X-Amz-Date': amz_date,
            'X-Amz-Target': amz_target,
            'Authorization': f'{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'
        }

        try:
            r = requests.post(endpoint_url, data=request_payload_str, headers=headers, timeout=10)
            if r.status_code != 200:
                raise Exception(f"Amazon API error: {r.status_code} - {r.text}")

            data = r.json()
            items = []
            for item in data.get("SearchResult", {}).get("Items", []):
                title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Senza titolo")
                url = item.get("DetailPageURL", "")
                price = None
                try:
                    price = item["Offers"]["Listings"][0]["Price"]["DisplayAmount"]
                except KeyError:
                    price = "N/D"

                items.append({
                    "title": title,
                    "url": url,
                    "price": price
                })

            return items
        except Exception as e:
            logger.error(e)
            return []
