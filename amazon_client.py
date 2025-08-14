print("🔍 DEBUG — Parametri di ricerca:")
print(f"  Keywords: {keyword}")
print(f"  Country: {self.country}")
print(f"  Resources: {self.resources}")
print(f"  Item Count: {item_count}")

try:
    response = self.api.search_items(
        Keywords=keyword,  # maiuscola K per compatibilità con amazon-paapi
        ItemCount=item_count,
        Resources=self.resources
    )

    print("📦 DEBUG — Risposta grezza da Amazon:")
    print(json.dumps(response, indent=2, ensure_ascii=False))

    # Salvataggio risposta grezza completa
    with open("amazon_raw.json", "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
    logger.info("💾 amazon_raw.json salvato con la risposta grezza di Amazon")
