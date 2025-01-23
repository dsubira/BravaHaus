from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Configuració de la base de dades
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ua1opglmi2dcvp:pb2846a65596ce3eaf1efe7be5ed91d369e1af83651c418d3a77c28920640634b@cah8ha8ra8h8i7.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d34184f0va5qsb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model de dades
class Immoble(db.Model):
    __tablename__ = 'immobles'
    id = db.Column(db.Integer, primary_key=True)
    titol = db.Column(db.String(255), nullable=False)
    descripcio = db.Column(db.Text)
    preu = db.Column(db.Numeric, nullable=False)
    ubicacio = db.Column(db.String(255))
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    habitacions = db.Column(db.Integer)
    banys = db.Column(db.Integer)
    m2 = db.Column(db.Float)
    immobiliaria = db.Column(db.String(255))
    fotos = db.Column(db.Text)  # Emmagatzema URLs separades per comes
    anotacions = db.Column(db.Text)

# Inicialitzar la base de dades
@app.before_first_request
def create_tables():
    db.create_all()

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')

# Ruta per llistar immobles
@app.route('/llistar-immobles')
def llistar_immobles():
    immobles = Immoble.query.all()
    return render_template('llistar_immobles.html', immobles=immobles)

# Ruta per afegir immobles manualment
@app.route('/afegir-immoble', methods=['GET', 'POST'])
def afegir_immoble():
    if request.method == 'POST':
        data = request.form

        # Geolocalització
        geolocator = Nominatim(user_agent="bravahaus")
        location = geolocator.geocode(data['ubicacio'])
        latitud = location.latitude if location else None
        longitud = location.longitude if location else None

        nou_immoble = Immoble(
            titol=data['titol'],
            descripcio=data['descripcio'],
            preu=data['preu'],
            ubicacio=data['ubicacio'],
            latitud=latitud,
            longitud=longitud,
            habitacions=data.get('habitacions', None),
            banys=data.get('banys', None),
            m2=data.get('m2', None),
            immobiliaria=data.get('immobiliaria', None),
            fotos=data.get('fotos', None),
            anotacions=data.get('anotacions', None)
        )

        db.session.add(nou_immoble)
        db.session.commit()
        return redirect(url_for('llistar_immobles'))

    return render_template('afegir_immoble.html')

# Ruta per afegir immobles des d'un enllaç
@app.route('/captura-enllac', methods=['POST'])
def captura_enllac():
    url = request.form['url']
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Captura d'informació específica (personalitzada per Fotocasa)
    titol = soup.find('h1').get_text(strip=True)
    preu = soup.find('span', class_='re-DetailHeader-price').get_text(strip=True).replace('€', '').replace('.', '')
    descripcio = soup.find('div', class_='re-DetailDescription-text').get_text(strip=True)
    ubicacio = soup.find('span', class_='re-DetailHeader-address-text').get_text(strip=True)

    # Altres camps específics
    habitacions = int(soup.find('span', class_='re-DetailFeatures-value').get_text(strip=True))
    banys = int(soup.find_all('span', class_='re-DetailFeatures-value')[1].get_text(strip=True))
    m2 = float(soup.find('span', class_='re-DetailFeatures-value').get_text(strip=True).replace('m²', '').strip())
    immobiliaria = soup.find('div', class_='re-ContactDetail-ownerName').get_text(strip=True)
    fotos = ','.join([img['src'] for img in soup.find_all('img', class_='re-DetailMediaPhoto')])

    # Geolocalització
    geolocator = Nominatim(user_agent="bravahaus")
    location = geolocator.geocode(ubicacio)
    latitud = location.latitude if location else None
    longitud = location.longitude if location else None

    # Afegir a la base de dades
    nou_immoble = Immoble(
        titol=titol,
        descripcio=descripcio,
        preu=preu,
        ubicacio=ubicacio,
        latitud=latitud,
        longitud=longitud,
        habitacions=habitacions,
        banys=banys,
        m2=m2,
        immobiliaria=immobiliaria,
        fotos=fotos
    )

    db.session.add(nou_immoble)
    db.session.commit()

    return jsonify({'message': 'Immoble capturat correctament!'})

if __name__ == '__main__':
    app.run(debug=True)
