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
    try:
        # Fer la petició HTTP
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()  # Llança un error si la resposta no és 200 OK
    except requests.RequestException as e:
        raise ValueError(f"Error en la petició a la URL: {e}")

    sopa = BeautifulSoup(resposta.text, 'html.parser')
    llistat_immobles = []

    # Funció per obtenir les dades d'un immoble
    def obtenir_immoble(element, adreca_cls, preu_cls, superficie_cls, habitacions_cls):
        try:
            adreca = element.find('span', class_=adreca_cls).text.strip()
            ciutat = adreca.split(',')[-1].strip() if ',' in adreca else adreca
            preu_text = element.find('span', class_=preu_cls).text.replace('€', '').replace('.', '').strip()
            preu = float(preu_text) if preu_text.isdigit() else None
            superficie_text = element.find('span', class_=superficie_cls).text.replace('m²', '').strip()
            superficie = float(superficie_text) if superficie_text.isdigit() else None
            habitacions_text = element.find('span', class_=habitacions_cls).text.strip()
            habitacions = int(habitacions_text) if habitacions_text.isdigit() else None

            # Només afegim l'immoble si té totes les dades necessàries
            if adreca and ciutat and preu and superficie and habitacions:
                return {
                    'adreca': adreca,
                    'ciutat': ciutat,
                    'preu': preu,
                    'superficie': superficie,
                    'habitacions': habitacions
                }
        except AttributeError:
            return None
        return None

    # Processar segons el portal
    if "fotocasa" in url:
        for element in sopa.find_all('div', class_='re-Card-pack'):
            immoble = obtenir_immoble(
                element,
                adreca_cls='re-Card-location',
                preu_cls='re-Card-price',
                superficie_cls='re-Card-size',
                habitacions_cls='re-Card-rooms'
            )
            if immoble:
                llistat_immobles.append(immoble)

    elif "idealista" in url:
        for element in sopa.find_all('article', class_='item'):
            immoble = obtenir_immoble(
                element,
                adreca_cls='item-location',
                preu_cls='item-price',
                superficie_cls='item-size',
                habitacions_cls='item-rooms'
            )
            if immoble:
                llistat_immobles.append(immoble)

    elif "habitaclia" in url:
        for element in sopa.find_all('div', class_='list-item'):
            immoble = obtenir_immoble(
                element,
                adreca_cls='list-location',
                preu_cls='list-price',
                superficie_cls='list-size',
                habitacions_cls='list-rooms'
            )
            if immoble:
                llistat_immobles.append(immoble)

    else:
        raise ValueError("El portal no està suportat actualment.")

    # Retornem la llista d'immobles
    return llistat_immobles

