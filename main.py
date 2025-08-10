from utils import cerca_prodotti, KEYWORDS

for parola in KEYWORDS:
    prodotti = cerca_prodotti(parola)
    print(f"Risultati per {parola}:")
    for p in prodotti:
        print(p)
