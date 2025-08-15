import logging
from amazon_client import AmazonClient

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("🔍 Recupero articoli da Amazon...")
    
    amazon_client = AmazonClient()  # Nessun parametro, prende tutto dalle secrets
    
    keywords = amazon_client.keywords
    logging.info(f"📜 Keywords lette dalle secrets: {keywords}")
    
    for keyword in keywords:
        items = amazon_client.search_items(keyword)
        logging.info(f"📦 Risultati trovati per '{keyword}': {len(items)}")
        for item in items:
            logging.info(f" - {item.get('title', 'Senza titolo')}")

if __name__ == "__main__":
    main()
