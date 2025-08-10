from utils import cerca_prodotti, KEYWORDS

if __name__ == "__main__":
    for keyword in KEYWORDS:
        print(f"🔍 Cerco prodotti per: {keyword}")
        prodotti = cerca_prodotti(keyword)
        for p in prodotti:
            print(p)
