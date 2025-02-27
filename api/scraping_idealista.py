import requests
from bs4 import BeautifulSoup
import re


class ScraperIdealista:
    """
    Scraper per extreure dades d'Idealista utilitzant l'API de ScraperAPI.
    """

    def __init__(self, api_key: str):
        """
        Inicialitza el scraper amb una API key.
        """
        self.api_key = api_key

    def fetch_page(self, url: str, render: bool = False) -> BeautifulSoup:
        """
        Fa una sol·licitud HTTP i retorna el contingut com un objecte BeautifulSoup.
        """
        payload = {
            'api_key': self.api_key,
            'url': url,
            'render': 'true' if render else 'false',
        }

        try:
            response = requests.get("https://api.scraperapi.com/", params=payload)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            raise Exception(f"Error obtenint la pàgina: {e}")

    def valida_url(self, url: str) -> bool:
        """
        Valida si l'URL proporcionat és d'Idealista.
        """
        return "idealista.com" in url

    def neteja_preu(self, preu_text: str) -> float:
        """
        Elimina símbols com '€' i tracta el punt com a separador de milers.
        """
        if preu_text:
            preu_netejat = re.sub(r"[^\d]", "", preu_text)  # Conserva només dígits
            return float(preu_netejat) if preu_netejat else None
        return None

    def neteja_superficie(self, superficie_text: str) -> float:
        """
        Elimina 'm²' i retorna el valor com un float.
        """
        if superficie_text:
            superficie_netejada = re.sub(r"[^\d.]", "", superficie_text)
            return float(superficie_netejada) if superficie_netejada else None
        return None

    def neteja_habitacions_banys(self, text: str) -> int:
        """
        Extreu el primer número d'un text (exemple: '1 bany' -> 1).
        """
        if text:
            match = re.search(r"\d+", text)
            return int(match.group()) if match else None
        return None

    def extreu_dades(self, url: str, premium: bool = False) -> dict:
        """
        Extreu les dades d'un immoble donada una URL d'Idealista.
        """
        if not self.valida_url(url):
            raise ValueError("L'URL proporcionat no és d'Idealista.")

        dades = {}  # Diccionari per emmagatzemar les dades
        try:
            soup = self.fetch_page(url, render=premium)

            # Captura de dades principals
            dades = {
                'títol': soup.select_one("span.main-info__title-main").text.strip()
                if soup.select_one("span.main-info__title-main")
                else "Sense títol",  # Valor per defecte si no es troba
                'preu': self.neteja_preu(
                    soup.select_one(".price").text.strip()
                ) if soup.select_one(".price") else None,
                'superficie_construida': self.neteja_superficie(
                    soup.select_one(".info-features span:nth-child(1)").text.strip()
                ) if soup.select_one(".info-features span:nth-child(1)") else None,
                'habitacions': self.neteja_habitacions_banys(
                    soup.select_one(".info-features span:nth-child(2)").text.strip()
                ) if soup.select_one(".info-features span:nth-child(2)") else None,
                'banys': self.neteja_habitacions_banys(
                    soup.select_one(".info-features span:nth-child(3)").text.strip()
                ) if soup.select_one(".info-features span:nth-child(3)") else None,
                'estat_conservacio': soup.find(text="Segona mà/bon estat").strip()
                if soup.find(text="Segona mà/bon estat")
                else None,
                'caracteristiques': "; ".join(
                    [el.text.strip() for el in soup.select(".details-property_features ul li")]
                )
                if soup.select(".details-property_features ul li")
                else None,
                'terrassa': "Sí" if "Terrassa" in soup.text or "balcó" in soup.text else "No",
                'piscina': "Sí" if "Piscina" in soup.text else "No",
                'aire_condicionat': "Sí" if "aire condicionat" in soup.text.lower() else "No",
                'parking': "Inclòs" if "Pàrking inclòs" in soup.text else "No inclòs",
                'ubicacio': soup.select_one(".main-info__title-minor").text.strip()
                if soup.select_one(".main-info__title-minor")
                else None,
                'descripcio': soup.select_one(".comment p").text.strip()
                if soup.select_one(".comment p")
                else None,
                'latitud': None,  # Placeholder per a coordenades
                'longitud': None,  # Placeholder per a coordenades
                'ubicacio_g': None,  # Placeholder per a punt geogràfic
                'portal': 'Idealista',
                'link': url,
                'certificat_energia': soup.select_one(".energy-certification").text.strip()
                if soup.select_one(".energy-certification")
                else None,
            }

            # Coordenades (si existeixen a la pàgina)
            coordenades = soup.select_one("#coordinates")
            if coordenades:
                try:
                    lat, lon = coordenades["data-lat"], coordenades["data-lon"]
                    dades["latitud"] = float(lat)
                    dades["longitud"] = float(lon)
                    dades["ubicacio_g"] = f"SRID=4326;POINT({lon} {lat})"
                except (KeyError, ValueError):
                    dades["ubicacio_g"] = "SRID=4326;POINT(0 0)"  # Valor per defecte

            # Si ubicacio_g continua sent None, s'assigna un valor predeterminat.
            if dades.get("ubicacio_g") is None:
                dades["ubicacio_g"] = "SRID=4326;POINT(0 0)"

            # Mostrem les dades capturades per depurar
            print("\n=== Dades extretes pel scraper abans d'inserir a la BD ===")
            for clau, valor in dades.items():
                print(f"{clau}: {valor}")

            return dades

        except Exception as e:
            # Mostrem l'error i les dades capturades en cas de fallada
            print("\n=== Error durant el scraping ===")
            print(f"Error: {e}")
            if dades:
                print("\nDades extretes fins al moment:")
                for clau, valor in dades.items():
                    print(f"{clau}: {valor}")
            return None


