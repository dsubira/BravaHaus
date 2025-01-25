from bs4 import BeautifulSoup
import requests

def extreure_dades_immobles(url):
    """
    Extreu dades d'immobles d'una URL d'un portal suportat.
    Suporta Fotocasa, Idealista i Habitaclia.

    Args:
        url (str): URL del portal immobiliari.

    Returns:
        list[dict]: Llista d'immobles amb les dades extretes.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Accept-Language": "ca-ES,ca;q=0.9,en;q=0.8",
    }

    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Error en la petició a la URL: {e}")

    if not resposta.headers.get("Content-Type", "").startswith("text/html"):
        raise ValueError(f"La URL no retorna HTML. Content-Type: {resposta.headers.get('Content-Type')}")

    sopa = BeautifulSoup(resposta.text, 'html.parser')
    llistat_immobles = []

    def obtenir_immoble(element, adreca_cls, preu_cls, superficie_cls, habitacions_cls):
        try:
            adreca = element.find("span", class_=adreca_cls).text.strip()
            ciutat = adreca.split(",")[-1].strip() if "," in adreca else adreca
            preu_text = element.find("span", class_=preu_cls).text.replace("€", "").replace(".", "").strip()
            preu = float(preu_text) if preu_text.isdigit() else None
            superficie_text = element.find("span", class_=superficie_cls).text.replace("m²", "").strip()
            superficie = float(superficie_text) if superficie_text.isdigit() else None
            habitacions_text = element.find("span", class_=habitacions_cls).text.strip()
            habitacions = int(habitacions_text) if habitacions_text.isdigit() else None

            if adreca and ciutat and preu and superficie and habitacions:
                return {
                    "adreca": adreca,
                    "ciutat": ciutat,
                    "preu": preu,
                    "superficie": superficie,
                    "habitacions": habitacions,
                }
        except AttributeError:
            return None
        return None

    if "fotocasa" in url:
        for element in sopa.find_all("div", class_="re-Card-pack"):
            immoble = obtenir_immoble(
                element, "re-Card-location", "re-Card-price", "re-Card-size", "re-Card-rooms"
            )
            if immoble:
                llistat_immobles.append(immoble)

    elif "idealista" in url:
        for element in sopa.find_all("article", class_="item"):
            immoble = obtenir_immoble(
                element, "item-location", "item-price", "item-size", "item-rooms"
            )
            if immoble:
                llistat_immobles.append(immoble)

    elif "habitaclia" in url:
        for element in sopa.find_all("div", class_="list-item"):
            immoble = obtenir_immoble(
                element, "list-location", "list-price", "list-size", "list-rooms"
            )
            if immoble:
                llistat_immobles.append(immoble)

    else:
        raise ValueError("El portal no està suportat actualment.")

    return llistat_immobles



if __name__ == "__main__":
    # Proves locals amb una URL exemple
    url_prova = "https://www.idealista.com/ca/inmueble/105879306/"
    try:
        immobles = extreure_dades_immobles(url_prova)
        print(f"Immobles extrets: {immobles}")
    except ValueError as e:
        print(f"Error: {e}")

