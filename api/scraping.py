import asyncio
import os
import subprocess
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


# Configura el camí perquè Playwright trobi els navegadors descarregats
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/app/.cache/ms-playwright"

# Verifica si els navegadors estan instal·lats, i si no, descarrega'ls
if not os.path.exists("/app/.cache/ms-playwright/chromium"):
    subprocess.run(["playwright", "install", "chromium"], check=True)


async def configurar_driver():
    """
    Configura Playwright amb el navegador Chrome en mode headless.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    return browser, playwright


async def obtenir_html(url):
    """
    Navega fins a una URL amb Playwright i retorna l'HTML renderitzat.
    """
    browser, playwright = await configurar_driver()
    try:
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(5)  # Esperar perquè es carregui tot el JavaScript
        return await page.content()
    except Exception as e:
        print(f"Error carregant la pàgina {url}: {e}")
        return None
    finally:
        await browser.close()
        await playwright.stop()


def analitzar_immobles(html, url):
    """
    Analitza l'HTML d'una pàgina de llistat d'immobles i retorna una llista d'immobles.
    """
    sopa = BeautifulSoup(html, 'html.parser')
    llistat_immobles = []

    try:
        if "fotocasa" in url:
            for element in sopa.find_all("article", class_="re-Card"):
                titol = element.find("span", class_="re-Card-title")
                preu = element.find("span", class_="re-Card-price")
                caracteristiques = element.find_all("li", class_="re-Card-feature")
                if titol and preu:
                    immoble = {
                        "titol": titol.text.strip(),
                        "preu": preu.text.strip(),
                        "caracteristiques": [el.text.strip() for el in caracteristiques],
                    }
                    llistat_immobles.append(immoble)

        elif "idealista" in url:
            for element in sopa.find_all("article", class_="item"):
                titol = element.find("a", class_="item-link")
                preu = element.find("span", class_="item-price")
                ubicacio = element.find("span", class_="item-detail")
                if titol and preu:
                    immoble = {
                        "titol": titol.text.strip(),
                        "preu": preu.text.strip(),
                        "ubicacio": ubicacio.text.strip() if ubicacio else None,
                    }
                    llistat_immobles.append(immoble)

        elif "habitaclia" in url:
            for element in sopa.find_all("div", class_="list-item"):
                titol = element.find("a", class_="property-title")
                preu = element.find("span", class_="price")
                ubicacio = element.find("div", class_="location")
                if titol and preu:
                    immoble = {
                        "titol": titol.text.strip(),
                        "preu": preu.text.strip(),
                        "ubicacio": ubicacio.text.strip() if ubicacio else None,
                    }
                    llistat_immobles.append(immoble)

    except Exception as e:
        print(f"Error analitzant la pàgina: {e}")

    return llistat_immobles


async def extreure_dades_immobles(url):
    """
    Extreu dades d'immobles des d'una URL d'un portal suportat.
    """
    html = await obtenir_html(url)
    if html:
        return analitzar_immobles(html, url)
    return []


async def extreure_dades_immoble_detall(url):
    """
    Extreu dades d'un immoble des d'una pàgina de detalls.
    """
    html = await obtenir_html(url)
    if not html:
        return None

    sopa = BeautifulSoup(html, 'html.parser')
    try:
        titol = sopa.find("h1", class_="re-DetailHeader-propertyTitle")
        preu = sopa.find("span", class_="re-DetailHeader-price")
        caracteristiques = sopa.find_all("li", class_="re-DetailHeader-features")

        if titol and preu:
            return {
                "titol": titol.text.strip(),
                "preu": preu.text.strip(),
                "caracteristiques": [el.text.strip() for el in caracteristiques],
            }
    except Exception as e:
        print(f"Error analitzant la pàgina de detalls: {e}")
        return None
