import os
from dotenv import load_dotenv
from amazon_api import get_amazon_products

load_dotenv()

def run_bot():
    print("🚀 Avvio bot Amazon...")

    # Leggi le variabili d'ambiente
    keywords = os.getenv("AMAZON_KEYWORDS")
    amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
    amazon_secret_key = os.getenv("AMAZON_SECRET_KEY")
    amazon_tag = os.getenv("AMAZON_TAG")
    amazon_region = os.getenv("AMAZON_REGION")
    amazon_host = os.getenv("AMAZON_HOST")

    if not all([keywords, amazon_access_key, amazon_secret_key, amazon_tag, amazon_region]):
        print("❌ Errore: una o più variabili d'ambiente mancanti.")
        return

    # Chiamata aggiornata con i nomi parametri corretti
    products = get_amazon_products(
        keywords=keywords,
        amazon_access_key=amazon_access_key,
        amazon_secret_key=amazon_secret_key,
        amazon_tag=amazon_tag,
        region=amazon_region,  # corretto da 'amazon_region'
        host=amazon_host
    )

    if not products:
        print("❌ Nessun prodotto trovato.")
        return

    print(f"✅ Trovati {len(products)} prodotti:")
    for product in products:
        print(f"- {product['title']} ({product['url']})")

if __name__ == "__main__":
    run_bot()
