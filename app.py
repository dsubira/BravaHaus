from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ua1opglmi2dcvp:pb2846a65596ce3eaf1efe7be5ed91d369e1af83651c418d3a77c28920640634b@cah8ha8ra8h8i7.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d34184f0va5qsb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model de la base de dades
class Immoble(db.Model):
    __tablename__ = 'immobles'
    id = db.Column(db.Integer, primary_key=True)
    titol = db.Column(db.String(255), nullable=False)
    descripcio = db.Column(db.Text)
    preu = db.Column(db.Numeric, nullable=False)
    ubicacio = db.Column(db.String(255))

@app.route('/afegir-immoble', methods=['GET', 'POST'])
def afegir_immoble():
    if request.method == 'POST':
        url = request.form.get('url')
        titol = request.form.get('titol')
        descripcio = request.form.get('descripcio')
        preu = request.form.get('preu')
        ubicacio = request.form.get('ubicacio')

        # Si hi ha URL, extreure dades automàticament
        if url:
            try:
                dades_extretes = extreu_dades_immoble(url)
                if dades_extretes:
                    titol = dades_extretes.get('titol', titol)
                    descripcio = dades_extretes.get('descripcio', descripcio)
                    preu = dades_extretes.get('preu', preu)
                    ubicacio = dades_extretes.get('ubicacio', ubicacio)
            except Exception as e:
                return jsonify({"error": f"No s'ha pogut processar l'URL: {e}"}), 400

        nou_immoble = Immoble(
            titol=titol,
            descripcio=descripcio,
            preu=preu,
            ubicacio=ubicacio
        )
        db.session.add(nou_immoble)
        db.session.commit()
        return redirect(url_for('get_immobles'))

    return render_template('afegir_immoble.html')

def extreu_dades_immoble(url):
    """Funció per extreure dades des d'un enllaç de Fotocasa o Habitaclia."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Exemples d'extracció per Fotocasa
    if 'fotocasa.es' in url:
        titol = soup.find('h1', class_='re-DetailHeader-propertyTitle').text.strip()
        descripcio = soup.find('div', class_='re-DetailFeatures-description').text.strip()
        preu = soup.find('span', class_='re-DetailHeader-price').text.strip().replace('€', '').replace('.', '')
        ubicacio = soup.find('span', class_='re-DetailHeader-address-text').text.strip()
        return {'titol': titol, 'descripcio': descripcio, 'preu': preu, 'ubicacio': ubicacio}

    # Exemples d'extracció per Habitaclia
    elif 'habitaclia.com' in url:
        titol = soup.find('h1', class_='info-title').text.strip()
        descripcio = soup.find('div', class_='adDescription').text.strip()
        preu = soup.find('span', class_='price').text.strip().replace('€', '').replace('.', '')
        ubicacio = soup.find('span', class_='address').text.strip()
        return {'titol': titol, 'descripcio': descripcio, 'preu': preu, 'ubicacio': ubicacio}

    else:
        raise ValueError("Només es permeten enllaços de Fotocasa i Habitaclia.")

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')

# Ruta per veure immobles
@app.route('/immobles', methods=['GET'])
def get_immobles():
    immobles = Immoble.query.all()
    return render_template('immobles.html', immobles=immobles)

if __name__ == '__main__':
    app.run(debug=True)

