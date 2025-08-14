import os
import json
import logging
from amazon_paapi import AmazonAPI

logger = logging.getLogger(__name__)

def mask_secret(value, visible_chars=3):
    """Maschera una secret lasciando visibili solo i primi N caratteri."""
    if not value:
        return "NON IMPOSTATA"
    return value[:visible_chars] + "*" * (len(value) - visible_chars)

class AmazonClient:
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.country = os.getenv("AMAZON_COUNTRY")
        self.resources = os.getenv("AMAZON_RESOURCES")

        # 🔍 Log iniziale credenziali mascherate
        logger.info("🛠️ Configurazione Amazon Client:")
        logger.info(f"  AMAZON_ACCESS_KEY: {mask_secret(self.access_key)}")
        logger.info(f"  AMAZON_SECRET_KEY: {mask_secret(self.secret_key)}")
        logger.info(f"  AMAZON_ASSOCIATE_TAG: {mask_secret(self.associate_tag)}")
        logger.info(f"  AMAZON_COUNTRY: {self.country}")
        logger.info(f"  AMAZON_RESOURCES: {self.resources}")

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

        # Debug parametri
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

            if "Errors" in response:
                logger.error(f"❌ Errore API Amazon: {response['Errors']}")
                raise ValueError(f"Errore API Amazon: {response['Errors']}")

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
