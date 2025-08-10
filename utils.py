import requests
import logging
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models import *

def cerca_prodotti(access_key, secret_key, associate_tag, country):
    # Imposta API Amazon
    from paapi5_python_sdk.api_client import ApiClient
    from paapi5_python_sdk.configuration import Configuration

    config = Configuration(
        access_key=access_key,
        secret_key=secret_key,
        host=f"webservices.amazon.{country}"
    )

    api_client = ApiClient(configuration=config)
    api = DefaultApi(api_client)

    # Categorie target
    keywords = ["infanzia", "bambini", "genitori", "scuola", "pannolini", "giocattoli"]

    request = SearchItemsRequest(
        partner_tag=associate_tag,
        partner_type="Associates",
        marketplace=f"www.amazon.{country}",
        keywords=" ".join(keywords),
        search_index="All",
        item_count=10
    )

    response = api.search_items(request)
    return response.search_result.items if response.search_result else []

def ha_offerte(prodotto):
    return hasattr(prodotto, "offers") and prodotto.offers is not None

def filtro_categoria(prodotto):
    categorie_target = ["infanzia", "bambini", "scuola", "pannolini", "giocattoli"]
    if hasattr(prodotto, "item_info") and hasattr(prodotto.item_info, "classifications"):
        classif = prodotto.item_info.classifications
        if hasattr(classif, "binding") and classif.binding and classif.binding.display_value:
            binding = classif.binding.display_value.lower()
            return any(cat in binding for cat in categorie_target)
    return False

def filtro_sconto(prodotto, minimo_percentuale):
    try:
        price = prodotto.offers.listings[0].price
        if price.savings and price.savings.percentage:
            return price.savings.percentage >= minimo_percentuale
    except Exception:
        pass
    return False

def filtro_lingua(prodotto, codice_lang="it"):
    try:
        if hasattr(prodotto, "item_info") and hasattr(prodotto.item_info, "languages"):
            langs = prodotto.item_info.languages.display_values
            return any(codice_lang in lang.value.lower() for lang in langs)
    except Exception:
        pass
    return True  # Se non c'è info lingua, non filtriamo
    return False

def formatta_messaggio(prodotto):
    titolo = prodotto.item_info.title.display_value if hasattr(prodotto.item_info, "title") else "Prodotto senza titolo"
    url = prodotto.detail_page_url
    prezzo = prodotto.offers.listings[0].price.display_amount if hasattr(prodotto.offers.listings[0].price, "display_amount") else "N/D"
    sconto = prodotto.offers.listings[0].price.savings.percentage if hasattr(prodotto.offers.listings[0].price, "savings") else 0

    return f"📌 {titolo}\n💰 Prezzo: {prezzo}\n📉 Sconto: {sconto}%\n🔗 {url}"

def invia_telegram(token, chat_id, messaggio):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": messaggio}
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        logging.error(f"Errore Telegram: {r.text}")
