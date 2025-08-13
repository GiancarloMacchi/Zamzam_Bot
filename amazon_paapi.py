import logging
import requests
import time
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.country = country.lower()

    def search_items(self, keywords):
        # Qui usiamo un mock API semplice per mantenere compatibilità
        # In produzione, sostituire con chiamata PAAPI firmata
        time.sleep(1)  # Evita chiamate troppo ravvicinate

        # Esempio di URL per test (mock)
        api_url = f"https://api.mocki.io/v1/b043df5a?keywords={quote(keywords)}"
        
        try:
            response = requests.get(api_url)
            if response.status_code != 200:
                raise Exception(f"Amazon API error: {response.status_code} - {response.text}")
            data = response.json()

            # Normalizza dati
            items = []
            for item in data.get("items", []):
                items.append({
                    "title": item.get("title", "Senza titolo"),
                    "url": item.get("url", "")
                })

            return items
        except Exception as e:
            logger.error(e)
            return []
