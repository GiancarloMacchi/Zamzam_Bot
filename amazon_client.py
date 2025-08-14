import os
import json
import logging
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

class AmazonClient:
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.country = os.getenv("AMAZON_COUNTRY")
        self.resources = os.getenv("AMAZON_RESOURCES")

        if not all([self.access_key, self.secret_key, self.associate_tag, self.country, self.resources]):
            raise ValueError("⚠️ Alcune variabili Amazon non sono impostate nelle Secret.")

        try:
            self.resources = json.loads(self.resources)
        except json.JSONDecodeError:
            raise ValueError("⚠️ AMAZON_RESOURCES non è un JSON valido.")

        self.api = AmazonAPI(
            self.access_key,
            self.secret_key,
            self.associate_tag,
            self.country
        )

    def search_items(self, keyword, item_count=10):
        logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

        # Debug: parametri
        print("🔍 DEBUG — Parametri di ricerca:")
        print(f"  Keywords: {keyword}")
        print(f"  Country: {self.country}")
        print(f"  Resources: {self.resources}")
        print(f"  Item Count: {item_count}")

        try:
            response = self.api.search_items(
                Keywords=keyword,
                ItemCount=item_count,
                Resources=self.resources
            )

            # Debug: risposta grezza
            print("📦 DEBUG — Risposta grezza da Amazon:")
            print(json.dumps(response, indent=2, ensure_ascii=False))

            # Controllo errori comuni Amazon API
            if "Errors" in response:
                logger.error(f"❌ Errore API Amazon: {response['Errors']}")
                raise ValueError(f"Errore API Amazon: {response['Errors']}")

            # Salvataggio risposta grezza
            with open("amazon_raw.json", "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            logger.info("💾 amazon_raw.json salvato con la risposta grezza di Amazon")

            if not response or "SearchResult" not in response or "Items" not in response["SearchResult"]:
                logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
                return []

            return response["SearchResult"]["Items"]

        except Exception as e:
            logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
            return []
