def search_amazon_items(amazon, keywords, item_count, min_save):
    results = []
    for keyword in keywords:
        try:
            response = amazon.search_items(
                keywords=keyword,
                item_count=item_count
            )
            for item in response["SearchResult"]["Items"]:
                title = item["ItemInfo"]["Title"]["DisplayValue"]
                url = item["DetailPageURL"]
                price_info = item["Offers"]["Listings"][0]["Price"]
                savings = item["Offers"]["Listings"][0].get("Savings", {}).get("Amount", 0)

                if savings >= min_save:
                    results.append({
                        "title": title,
                        "url": url,
                        "price": price_info["DisplayAmount"],
                        "savings": savings
                    })
        except Exception as e:
            print(f"Errore nella ricerca per '{keyword}': {e}")
    return results
