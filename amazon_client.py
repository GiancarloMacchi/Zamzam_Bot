import json
import bottlenose
from bs4 import BeautifulSoup
import requests

class AmazonClient:
    def __init__(self, access_key, secret_key, associate_tag, region="IT"):
        self.client = bottlenose.Amazon(
            AWSAccessKeyId=access_key,
            AWSSecretAccessKey=secret_key,
            AssociateTag=associate_tag,
            Region=region
        )

    def get_items(self, keywords, item_count=10, min_save=0):
        try:
            response = self.client.ItemSearch(
                Keywords=keywords,
                SearchIndex="All",
                ResponseGroup="Large",
                ItemPage=1
            )

            # Convert response to dict if needed
            if hasattr(response, "to_json"):
                raw_json = json.loads(response.to_json())
            elif isinstance(response, str):
                raw_json = json.loads(response)
            else:
                raw_json = response

            # 💾 Salva risposta grezza
            with open("amazon_raw_response.json", "w", encoding="utf-8") as raw_file:
                json.dump(raw_json, raw_file, ensure_ascii=False, indent=4)
            print("💾 File amazon_raw_response.json salvato (risposta grezza Amazon API).")

            # Parsing XML
            soup = BeautifulSoup(response, "xml")
            items = []

            for item in soup.find_all("Item")[:item_count]:
                try:
                    title = item.Title.text if item.Title else "No title"
                    url = item.DetailPageURL.text if item.DetailPageURL else ""
                    price = None
                    savings = 0

                    if item.ListPrice and item.ListPrice.Amount:
                        price = int(item.ListPrice.Amount.text) / 100

                    if item.OfferSummary and item.OfferSummary.LowestNewPrice:
                        lowest_price = int(item.OfferSummary.LowestNewPrice.Amount.text) / 100
                        if price:
                            savings = round(((price - lowest_price) / price) * 100, 2)
                        price = lowest_price

                    if savings >= min_save:
                        items.append({
                            "title": title,
                            "url": url,
                            "price": price,
                            "savings": savings
                        })
                except Exception as e:
                    print(f"Errore parsing item: {e}")

            return items

        except Exception as e:
            print(f"Errore nella richiesta Amazon API: {e}")
            return []
