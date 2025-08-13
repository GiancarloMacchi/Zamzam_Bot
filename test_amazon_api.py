import os
from dotenv import load_dotenv
from amazon_paapi import AmazonApi

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY", "IT")

print("\n=== TEST AMAZON PA-API ===")
print(f"ACCESS_KEY: {ACCESS_KEY[:4] if ACCESS_KEY else 'None'}... ({len(ACCESS_KEY) if ACCESS_KEY else 0} chars)")
print(f"SECRET_KEY: {SECRET_KEY[:4] if SECRET_KEY else 'None'}... ({len(SECRET_KEY) if SECRET_KEY else 0} chars)")
print(f"ASSOCIATE_TAG: {ASSOCIATE_TAG}")
print(f"COUNTRY: {COUNTRY}")
print("==========================\n")

try:
    amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)
    results = amazon.search_items(keywords="laptop", item_count=1)
    items = []
    if hasattr(results, "items"):
        items = results.items
    elif results:
        items = list(results)
    if items:
        item0 = items[0]
        title = getattr(item0, "title", None) or getattr(getattr(getattr(item0, "item_info", None), "title", None), "display_value", None)
        print("✅ API OK. Titolo:", title or "(sconosciuto)")
    else:
        print("⚠ API risponde ma nessun item.")
except Exception as e:
    err = str(e)
    print("❌ Errore API:", err)
    if "InvalidAssociate" in err:
        print("➡ Il tuo Associate Tag NON è attivo per PA-API.")
    elif "InternalFailure" in err or "InternalError" in err:
        print("➡ Credenziali valide ma accesso PA-API probabilmente non abilitato.")
    elif "Forbidden" in err or "AccessDenied" in err:
        print("➡ Le chiavi non hanno i permessi per PA-API.")
    elif "TooManyRequests" in err or "throttle" in err.lower():
        print("➡ Limite TPD/TPS raggiunto.")
    else:
        print("➡ Errore generico. Verifica regione/marketplace e tag.")

print("\nTest completato.\n")
