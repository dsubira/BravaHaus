from bs4 import BeautifulSoup
import requests


def extreure_dades_immobles(url):
    """
    Extreu dades d'immobles d'una URL d'un portal suportat (llistats).
    Suporta Fotocasa.

    Args:
        url (str): URL del portal immobiliari.

    Returns:
        list[dict]: Llista d'immobles amb les dades extretes.

    Raises:
        ValueError: Si hi ha errors en la petició o el portal no està suportat.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
        "Accept-Language": "ca-ES,ca;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
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

    # Processar immobles d'un llistat
    if "fotocasa" in url:
        for element in sopa.find_all("article", class_="re-Card"):
            try:
                titol = element.find("span", class_="re-Card-title").text.strip()
                preu = element.find("span", class_="re-Card-price").text.strip()
                caracteristiques = [el.text.strip() for el in element.find_all("li", class_="re-Card-feature")]
                fotos = [img["src"] for img in element.find_all("img", class_="re-Card-image")]

                immoble = {
                    "titol": titol,
                    "preu": preu,
                    "caracteristiques": caracteristiques,
                    "fotos": fotos,
                }
                llistat_immobles.append(immoble)
            except AttributeError:
                continue
    else:
        raise ValueError("El portal no està suportat actualment.")

    return llistat_immobles


def extreure_dades_immoble_detall(url):
    """
    Extreu dades d'un immoble des d'una pàgina de detalls a Fotocasa.

    Args:
        url (str): URL de la pàgina de l'immoble.

    Returns:
        dict: Dades extretes de l'immoble.

    Raises:
        ValueError: Si hi ha errors en la petició o si no es poden extreure dades.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
        "Accept-Language": "ca-ES,ca;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()

        # Diagnòstic: guardar l'HTML en un fitxer local
        with open("pagina.html", "w", encoding="utf-8") as fitxer:
            fitxer.write(resposta.text)

    except requests.RequestException as e:
        raise ValueError(f"Error en la petició a la URL: {e}")

    if not resposta.headers.get("Content-Type", "").startswith("text/html"):
        raise ValueError(f"La URL no retorna HTML. Content-Type: {resposta.headers.get('Content-Type')}")

    sopa = BeautifulSoup(resposta.text, 'html.parser')

    # Extreure dades de l'immoble
    try:
        titol = sopa.find("h1", class_="re-DetailHeader-propertyTitle").text.strip()
        preu = sopa.find("span", class_="re-DetailHeader-price").text.strip()
        caracteristiques = [el.text.strip() for el in sopa.find_all("li", class_="re-DetailHeader-features")]
        tipus = sopa.find("div", class_="re-DetailFeaturesList-featureLabel").text.strip()
        certificat_energia = sopa.find("div", class_="re-DetailEnergyCertificate-item").text.strip()
        poblacio = sopa.find("div", class_="re-DetailLocation-area").text.strip()
        fotos = [img["src"] for img in sopa.find_all("img", class_="re-DetailGallery-image")]

    except AttributeError as e:
        raise ValueError(f"No s'han pogut extreure algunes dades: {e}")

    return {
        "titol": titol,
        "preu": preu,
        "caracteristiques": caracteristiques,
        "tipus": tipus,
        "certificat_energia": certificat_energia,
        "poblacio": poblacio,
        "fotos": fotos,
    }


if __name__ == "__main__":
    prova_url = "https://www.fotocasa.es/ca/comprar/vivenda/torroella-de-montgri/aire-condicionat-no-moblat/185360406/d"

    try:
        dades_immoble = extreure_dades_immoble_detall(prova_url)
        print("Dades extretes:")
        print(dades_immoble)
    except ValueError as e:
        print(f"Error: {e}")

