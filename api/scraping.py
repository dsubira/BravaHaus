from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import time


def configurar_driver():
    """
    Configura el controlador de Selenium amb opcions adequades.
    """
    options = Options()
    options.add_argument("--headless")  # Executar en mode headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Substitueix '/path/to/chromedriver' amb la ruta al teu executable de Chromedriver
    service = Service("/path/to/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def extreure_dades_immobles(url):
    """
    Extreu dades d'immobles d'una URL d'un portal suportat (llistats).
    Suporta Fotocasa.
    """
    driver = configurar_driver()
    try:
        print(f"Processant URL (llistat): {url}")
        driver.get(url)
        time.sleep(5)  # Espera a que es carregui el JavaScript

        # Obtenir l'HTML renderitzat
        html = driver.page_source

        # Guardar l'HTML de depuració (opcional)
        with open("llistat_debug.html", "w", encoding="utf-8") as fitxer:
            fitxer.write(html)

        sopa = BeautifulSoup(html, 'html.parser')
        llistat_immobles = []

        # Processar immobles del llistat
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

        return llistat_immobles
    finally:
        driver.quit()


def extreure_dades_immoble_detall(url):
    """
    Extreu dades d'un immoble des d'una pàgina de detalls a Fotocasa.
    """
    driver = configurar_driver()
    try:
        print(f"Processant URL (detall): {url}")
        driver.get(url)
        time.sleep(5)  # Espera a que es carregui el JavaScript

        # Obtenir l'HTML renderitzat
        html = driver.page_source

        # Guardar l'HTML de depuració (opcional)
        with open("detall_debug.html", "w", encoding="utf-8") as fitxer:
            fitxer.write(html)

        sopa = BeautifulSoup(html, 'html.parser')

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
    finally:
        driver.quit()


if __name__ == "__main__":
    # Proves
    prova_llistat = "https://www.fotocasa.es"
    prova_detall = "https://www.fotocasa.es/ca/comprar/vivenda/torroella-de-montgri/calefaccio-parking-jardi-terrassa-no-moblat/185192418/d"

    try:
        print("Prova llistat:")
        immobles = extreure_dades_immobles(prova_llistat)
        print(immobles)

        print("\nProva detall:")
        immoble = extreure_dades_immoble_detall(prova_detall)
        print(immoble)
    except ValueError as e:
        print(f"Error: {e}")

