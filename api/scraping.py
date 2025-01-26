from bs4 import BeautifulSoup
import requests

def extreure_dades_immobles(url):
    """
    Extreu dades d'immobles d'una URL d'un portal suportat.
    Suporta Fotocasa, Idealista i altres portals amb estructura predefinida.

    Args:
        url (str): URL del portal immobiliari.

    Returns:
        list[dict]: Llista d'immobles amb les dades extretes.

    Raises:
        ValueError: Si hi ha errors en la petició o el portal no està suportat.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Accept-Language": "ca-ES,ca;q=0.9,en;q=0.8",
    }

    try:
        # Fer la petició HTTP
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()  # Llança un error si la resposta no és 200 OK
    except requests.RequestException as e:
        raise ValueError(f"Error en la petició a la URL: {e}")

    # Comprovar que la resposta és HTML
    if not resposta.headers.get("Content-Type", "").startswith("text/html"):
        raise ValueError(f"La URL no retorna HTML. Content-Type: {resposta.headers.get('Content-Type')}")

    # Analitzar el contingut HTML
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    llistat_immobles = []

    # Funció auxiliar per extreure dades d'un immoble
    def obtenir_immoble(element, adreca_cls, preu_cls, superficie_cls, habitacions_cls):
        """
        Extreu les dades d'un element HTML d'immoble.

        Args:
            element: Element HTML que conté dades d'un immoble.
            adreca_cls (str): Classe CSS per a l'adreça.
            preu_cls (str): Classe CSS per al preu.
            superficie_cls (str): Classe CSS per a la superfície.
            habitacions_cls (str): Classe CSS per a les habitacions.

        Returns:
            dict o None: Retorna un diccionari amb les dades si es troben, sinó None.
        """
        try:
            adreca = element.find("span", class_=adreca_cls).text.strip()
            ciutat = adreca.split(",")[-1].strip() if "," in adreca else adreca
            preu_text = element.find("span", class_=preu_cls).text.replace("€", "").replace(".", "").strip()
            preu = float(preu_text) if preu_text.isdigit() else None
            superficie_text = element.find("span", class_=superficie_cls).text.replace("m²", "").strip()
            superficie = float(superficie_text) if superficie_text.isdigit() else None
            habitacions_text = element.find("span", class_=habitacions_cls).text.strip()
            habitacions = int(habitacions_text) if habitacions_text.isdigit() else None

            # Només afegim l'immoble si totes les dades són vàlides
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

    # Processar segons el portal
    if "fotocasa" in url:
        for element in sopa.find_all("div", class_="re-Card-pack"):
            immoble = obtenir_immoble(
                element, 
                adreca_cls="re-Card-location", 
                preu_cls="re-Card-price", 
                superficie_cls="re-Card-size", 
                habitacions_cls="re-Card-rooms"
            )
            if immoble:
                llistat_immobles.append(immoble)

    elif "idealista" in url:
        for element in sopa.find_all("article", class_="item"):
            immoble = obtenir_immoble(
                element, 
                adreca_cls="item-location", 
                preu_cls="item-price", 
                superficie_cls="item-size", 
                habitacions_cls="item-rooms"
            )
            if immoble:
                llistat_immobles.append(immoble)

    else:
        raise ValueError("El portal no està suportat actualment.")

    # Retornar la llista d'immobles extrets
    return llistat_immobles


if __name__ == "__main__":
    # Test local amb una URL de prova
    prova_url = "https://www.fotocasa.es"
    try:
        immobles = extreure_dades_immobles(prova_url)
        print(f"Immobles extrets: {immobles}")
    except ValueError as e:
        print(f"Error: {e}")

