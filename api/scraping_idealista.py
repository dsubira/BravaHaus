import requests
from bs4 import BeautifulSoup


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

    def extreu_dades(self, url: str, premium: bool = False) -> dict:
        """
        Extreu les dades d'un immoble donada una URL d'Idealista.
        """
        try:
            soup = self.fetch_page(url, render=premium)

            # Diccionari per emmagatzemar les dades extretes
            dades = {
                'títol': soup.select_one("h1.main-info__title-main").text.strip()
                if soup.select_one("h1.main-info__title-main")
                else None,
                'preu': soup.select_one(".price").text.strip()
                if soup.select_one(".price")
                else None,
                'superficie_construida': soup.select_one(".info-features span:nth-child(1)").text.strip()
                if soup.select_one(".info-features span:nth-child(1)")
                else None,
                'habitacions': soup.select_one(".info-features span:nth-child(2)").text.strip()
                if soup.select_one(".info-features span:nth-child(2)")
                else None,
                'banys': soup.select_one(".info-features span:nth-child(3)").text.strip()
                if soup.select_one(".info-features span:nth-child(3)")
                else None,
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
                    pass

            return dades

        except Exception as e:
            print(f"Error durant l'extracció: {e}")
            return None


