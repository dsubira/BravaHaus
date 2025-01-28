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
                else "Títol no disponible",
                'preu': soup.select_one(".price").text.strip()
                if soup.select_one(".price")
                else "Preu no disponible",
                'superficie_construida': soup.select_one(".info-features span:nth-child(1)").text.strip()
                if soup.select_one(".info-features span:nth-child(1)")
                else "Superfície no disponible",
                'habitacions': soup.select_one(".info-features span:nth-child(2)").text.strip()
                if soup.select_one(".info-features span:nth-child(2)")
                else "Nombre d'habitacions no disponible",
                'banys': soup.select_one(".info-features span:nth-child(3)").text.strip()
                if soup.select_one(".info-features span:nth-child(3)")
                else "Nombre de banys no disponible",
                'estat_conservacio': soup.find(text="Segona mà/bon estat").strip()
                if soup.find(text="Segona mà/bon estat")
                else "Estat de conservació no disponible",
                'terrassa': "Sí"
                if "Terrassa" in soup.text or "balcó" in soup.text
                else "No",
                'piscina': "Sí" if "Piscina" in soup.text else "No",
                'aire_condicionat': "Sí" if "aire condicionat" in soup.text.lower() else "No",
                'parking': "Inclòs"
                if soup.find(text="Pàrking inclòs")
                else "No inclòs",
                'districte': soup.select_one(".main-info__title-minor").text.strip()
                if soup.select_one(".main-info__title-minor")
                else "Districte no disponible",
                'descripcio': soup.select_one(".comment p").text.strip()
                if soup.select_one(".comment p")
                else "Descripció no disponible",
                'preu_per_m2': soup.select_one(".squaredmeterprice .flex-feature-details").text.strip()
                if soup.select_one(".squaredmeterprice .flex-feature-details")
                else "Preu per m² no disponible",
            }

            # Certificat energètic
            certificat = soup.select_one(".details-property-feature-two .details-property_features ul")
            if certificat:
                try:
                    consum = certificat.find_all("li")[0].text.split(":")[1].strip() if "Consum" in certificat.text else "No disponible"
                except (IndexError, AttributeError):
                    consum = "No disponible"

                try:
                    emissions = certificat.find_all("li")[1].text.split(":")[1].strip() if "Emissions" in certificat.text else "No disponible"
                except (IndexError, AttributeError):
                    emissions = "No disponible"

                dades['consum_energia'] = consum
                dades['emissions_energia'] = emissions
            else:
                dades['consum_energia'] = "No disponible"
                dades['emissions_energia'] = "No disponible"

            return dades

        except Exception as e:
            print(f"Error durant l'extracció: {e}")
            return None
