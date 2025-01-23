from bs4 import BeautifulSoup
import requests

def extreure_fotocasa(url):
    resposta = requests.get(url)
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    llistat_immobles = []

    for element in sopa.find_all('article', class_='re-Card'):  # Exemple de classe CSS per Fotocasa
        adreca = element.find('span', class_='re-Card-title').text if element.find('span', class_='re-Card-title') else 'Desconeguda'
        ciutat = element.find('span', class_='re-Card-city').text if element.find('span', class_='re-Card-city') else 'Desconeguda'
        preu = float(element.find('span', class_='re-Card-price').text.replace('€', '').replace(',', '')) if element.find('span', class_='re-Card-price') else 0
        superficie = float(element.find('span', class_='re-Card-surface').text.replace('m²', '').strip()) if element.find('span', class_='re-Card-surface') else 0
        habitacions = int(element.find('span', class_='re-Card-rooms').text.strip()) if element.find('span', class_='re-Card-rooms') else 0

        llistat_immobles.append({
            'adreca': adreca,
            'ciutat': ciutat,
            'preu': preu,
            'superficie': superficie,
            'habitacions': habitacions
        })

    return llistat_immobles

def extreure_idealista(url):
    resposta = requests.get(url)
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    llistat_immobles = []

    for element in sopa.find_all('div', class_='item-info-container'):  # Exemple de classe CSS per Idealista
        adreca = element.find('a', class_='item-link').text if element.find('a', class_='item-link') else 'Desconeguda'
        ciutat = element.find('span', class_='item-location').text if element.find('span', class_='item-location') else 'Desconeguda'
        preu = float(element.find('span', class_='item-price').text.replace('€', '').replace('.', '').strip()) if element.find('span', class_='item-price') else 0
        superficie = float(element.find('span', class_='item-size').text.replace('m²', '').strip()) if element.find('span', class_='item-size') else 0
        habitacions = int(element.find('span', class_='item-rooms').text.strip()) if element.find('span', class_='item-rooms') else 0

        llistat_immobles.append({
            'adreca': adreca,
            'ciutat': ciutat,
            'preu': preu,
            'superficie': superficie,
            'habitacions': habitacions
        })

    return llistat_immobles

def extreure_habitaclia(url):
    resposta = requests.get(url)
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    llistat_immobles = []

    for element in sopa.find_all('div', class_='listing-item'):  # Exemple de classe CSS per Habitaclia
        adreca = element.find('a', class_='address').text if element.find('a', class_='address') else 'Desconeguda'
        ciutat = element.find('span', class_='city').text if element.find('span', class_='city') else 'Desconeguda'
        preu = float(element.find('span', class_='price').text.replace('€', '').replace('.', '').strip()) if element.find('span', class_='price') else 0
        superficie = float(element.find('span', class_='surface').text.replace('m²', '').strip()) if element.find('span', class_='surface') else 0
        habitacions = int(element.find('span', class_='rooms').text.strip()) if element.find('span', class_='rooms') else 0

        llistat_immobles.append({
            'adreca': adreca,
            'ciutat': ciutat,
            'preu': preu,
            'superficie': superficie,
            'habitacions': habitacions
        })

    return llistat_immobles

def extreure_dades_immobles(portal, url):
    if portal == 'fotocasa':
        return extreure_fotocasa(url)
    elif portal == 'idealista':
        return extreure_idealista(url)
    elif portal == 'habitaclia':
        return extreure_habitaclia(url)
    else:
        raise ValueError(f'Portal desconegut: {portal}')
