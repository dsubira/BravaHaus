from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def configurar_driver():
    # Assegura que el Chromedriver estigui instal·lat
    chromedriver_autoinstaller.install()  # Automàticament gestiona la versió correcta
    
    # Configura Chrome en mode headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # Inicia el driver amb les opcions configurades
    driver = webdriver.Chrome(options=chrome_options)
    return driver
