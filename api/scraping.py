from bs4 import BeautifulSoup
import requests

def extreure_dades_immobles(url):
    resposta = requests.get(url)
    sopa = BeautifulSoup(resposta.text, 'html.parser')

    llistat_immobles = []

    def obtenir_immoble(element, adreca_cls, preu_cls, superficie_cls, habitacions_cls):
        try:
            adreca = element.find('span', class_=adreca_cls).text.strip()
            ciutat = adreca.split(',')[-1].strip() if ',' in adreca else adreca
            preu = float(element.find('span', class_=preu_cls).text.replace('€', '').replace('.', '').strip())
            superficie = float(element.find('span', class_=superficie_cls).text.replace('m²', '').strip())
            habitacions = int(element.find('span', class_=habitacions_cls).text.strip())
            return {
                'adreca': adreca,
                'ciutat': ciutat,
                'preu': preu,
                'superficie': superficie,
                'habitacions': habitacions
            }
        except AttributeError:
            return None

    # Identificar el portal segons la URL
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

    return llistat_immobles
