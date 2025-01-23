from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
db = SQLAlchemy(app)

class Immoble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    address = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    price = db.Column(db.String(50))
    rooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    area = db.Column(db.Float)
    agency = db.Column(db.String(100))
    link = db.Column(db.String(300))
    notes = db.Column(db.Text)

# Funció per inicialitzar el sistema
def initialize():
    with app.app_context():
        db.create_all()

initialize()

def scrape_fotocasa(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1', class_='re-DetailHeader-propertyTitle').get_text(strip=True)
    address = soup.find('span', class_='re-DetailHeader-address-text').get_text(strip=True)
    price = soup.find('span', class_='re-DetailHeader-price').get_text(strip=True)
    details = soup.find_all('li', class_='re-DetailFeaturesList-feature')

    rooms = None
    bathrooms = None
    area = None
    for detail in details:
        text = detail.get_text(strip=True)
        if 'hab.' in text:
            rooms = int(text.split(' ')[0])
        elif 'baños' in text:
            bathrooms = int(text.split(' ')[0])
        elif 'm²' in text:
            area = float(text.split(' ')[0])

    agency_tag = soup.find('div', class_='re-ContactDetail-realEstateName')
    agency = agency_tag.get_text(strip=True) if agency_tag else None

    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    latitude = location.latitude if location else None
    longitude = location.longitude if location else None

    return {
        'title': title,
        'address': address,
        'latitude': latitude,
        'longitude': longitude,
        'price': price,
        'rooms': rooms,
        'bathrooms': bathrooms,
        'area': area,
        'agency': agency,
        'link': url
    }

@app.route('/')
def index():
    immobles = Immoble.query.all()
    return render_template('llistar_immobles.html', immobles=immobles)

@app.route('/afegir', methods=['GET', 'POST'])
def afegir():
    if request.method == 'POST':
        link = request.form['link']
        notes = request.form.get('notes', '')
        data = scrape_fotocasa(link)

        nou_immoble = Immoble(
            title=data['title'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            price=data['price'],
            rooms=data['rooms'],
            bathrooms=data['bathrooms'],
            area=data['area'],
            agency=data['agency'],
            link=data['link'],
            notes=notes
        )

        db.session.add(nou_immoble)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('afegir_immoble.html')

if __name__ == '__main__':
    app.run(debug=True)
