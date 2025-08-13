import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
COUNTRY = os.getenv("AMAZON_COUNTRY")

print("\n=== TEST AMAZON PA-API ===")
print(f"ACCESS_KEY: {ACCESS_KEY[:4]}... ({len(ACCESS_KEY)} chars)")
print(f"SECRET_KEY: {SECRET_KEY[:4]}... ({len(SECRET_KEY)} chars)")
print(f"ASSOCIATE_TAG: {ASSOCIATE_TAG}")
print(f"COUNTRY: {COUNTRY}")
print("==========================\n")

try:
    amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)
    results = amazon.search_items(keywords="laptop", item_count=1)
    print("✅ Risultato API ricevuto.")
    if hasattr(results, "items") and results.items:
        print(f"Titolo prodotto: {results.items[0].item_info.title.display_value}")
    else:
        print("⚠ Nessun prodotto trovato, ma API funzionante.")
except Exception as e:
    err = str(e)
    print("❌ Errore API:", err)

    if "InvalidAssociate" in err:
        print("➡ Il tuo Associate Tag NON è attivo per PA-API.")
    elif "InternalFailure" in err:
        print("➡ Credenziali valide, ma l'account NON ha accesso attivo alla PA-API.")
    elif "InvalidParameterValue" in err:
        print("➡ Probabile errore nel parametro COUNTRY o nella query.")
    elif "Forbidden" in err:
        print("➡ Le chiavi non hanno i permessi per usare le PA-API.")
    else:
        print("➡ Errore generico. Controlla la configurazione e i permessi.")

print("\nTest completato.\n")
