from utils import cerca_prodotti, KEYWORDS

def main():
    for keyword in KEYWORDS:
        print(f"🔍 Ricerca: {keyword}")
        cerca_prodotti(keyword)

if __name__ == "__main__":
    main()
