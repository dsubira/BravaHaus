from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def configurar_driver():
    """
    Configura el driver de Selenium utilitzant chromedriver-autoinstaller.
    """
    # Instal·la automàticament Chromedriver compatible
    chromedriver_autoinstaller.install()

    # Configura les opcions de Chrome
    options = Options()
    options.add_argument("--headless")  # Executa Chrome en mode headless
    options.add_argument("--disable-gpu")  # Desactiva la GPU per entorns remots
    options.add_argument("--no-sandbox")  # Evita problemes en entorns sandbox
    options.add_argument("--disable-dev-shm-usage")  # Utilitza la memòria compartida de manera eficient

    # Retorna el navegador configurat
    driver = webdriver.Chrome(options=options)
    return driver

