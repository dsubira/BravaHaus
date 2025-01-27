import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import subprocess

# Descarrega els navegadors necessaris abans de començar
subprocess.run(["playwright", "install", "chromium"], check=True)
import os

# Configura el camí perquè Playwright trobi els navegadors descarregats
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/app/.cache/ms-playwright"


async def configurar_driver():
    """
    Configura Playwright amb el navegador Chrome en mode headless.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)  # Mode headless
    return browser, playwright

async def extreure_dades_immobles(url):
    """
    Extreu dades d'immobles des d'una URL d'un portal suportat (llistats).
    Suporta Fotocasa, Idealista i Habitaclia.
    """
    browser, playwright = await configurar_driver()
    try:
        print(f"Processant URL (llistat): {url}")
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(5)  # Esperar perquè es carregui el JavaScript complet

        # Obtenir l'HTML renderitzat
        html = await page.content()
        sopa = BeautifulSoup(html, 'html.parser')
        llistat_immobles = []

        if "fotocasa" in url:
            for element in sopa.find_all("article", class_="re-Card"):
                try:
                    titol = element.find("span", class_="re-Card-title").text.strip()
                    preu = element.find("span", class_="re-Card-price").text.strip()
                    caracteristiques = [el.text.strip() for el in element.find_all("li", class_="re-Card-feature")]

                    immoble = {
                        "titol": titol,
                        "preu": preu,
                        "caracteristiques": caracteristiques,
                    }
                    llistat_immobles.append(immoble)
                except AttributeError:
                    continue

        elif "idealista" in url:
            for element in sopa.find_all("article", class_="item"):
                try:
                    titol = element.find("a", class_="item-link").get_text(strip=True)
                    preu = element.find("span", class_="item-price").get_text(strip=True)
                    ubicacio = element.find("span", class_="item-detail").get_text(strip=True)

                    immoble = {
                        "titol": titol,
                        "preu": preu,
                        "ubicacio": ubicacio,
                    }
                    llistat_immobles.append(immoble)
                except AttributeError:
                    continue

        elif "habitaclia" in url:
            for element in sopa.find_all("div", class_="list-item"):
                try:
                    titol = element.find("a", class_="property-title").get_text(strip=True)
                    preu = element.find("span", class_="price").get_text(strip=True)
                    ubicacio = element.find("div", class_="location").get_text(strip=True)

                    immoble = {
                        "titol": titol,
                        "preu": preu,
                        "ubicacio": ubicacio,
                    }
                    llistat_immobles.append(immoble)
                except AttributeError:
                    continue

        return llistat_immobles
    finally:
        await browser.close()
        await playwright.stop()

async def extreure_dades_immoble_detall(url):
    """
    Extreu dades d'un immoble des d'una pàgina de detalls (Fotocasa).
    """
    browser, playwright = await configurar_driver()
    try:
        print(f"Processant URL (detall): {url}")
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(5)  # Esperar perquè es carregui el JavaScript complet

        # Obtenir l'HTML renderitzat
        html = await page.content()
        sopa = BeautifulSoup(html, 'html.parser')

        titol = sopa.find("h1", class_="re-DetailHeader-propertyTitle").text.strip()
        preu = sopa.find("span", class_="re-DetailHeader-price").text.strip()
        caracteristiques = [el.text.strip() for el in sopa.find_all("li", class_="re-DetailHeader-features")]

        immoble = {
            "titol": titol,
            "preu": preu,
            "caracteristiques": caracteristiques,
        }

        return immoble
    finally:
        await browser.close()
        await playwright.stop()
