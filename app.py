from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configuració de la base de dades (substitueix amb DATABASE_URL real)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ua1opglmi2dcvp:pb2846a65596ce3eaf1efe7be5ed91d369e1af83651c418d3a77c28920640634b@cah8ha8ra8h8i7.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d34184f0va5qsb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Exemple de model
class Immoble(db.Model):
    __tablename__ = 'immobles'
    id = db.Column(db.Integer, primary_key=True)
    titol = db.Column(db.String(255), nullable=False)
    descripcio = db.Column(db.Text)
    preu = db.Column(db.Numeric, nullable=False)
    ubicacio = db.Column(db.String(255))

# Ruta per al formulari
@app.route('/afegir_immoble', methods=['GET', 'POST'])
def afegir_immoble():
    if request.method == 'POST':
        url = request.form['url']
        
        # Realitzar el scraping
        dades = extreure_dades(url)
        
        # Comprovar si hi ha resultats
        if dades:
            nou_immoble = Immoble(
                titol=dades['titol'],
                descripcio=dades['descripcio'],
                preu=dades['preu'],
                ubicacio=dades['ubicacio']
            )
            db.session.add(nou_immoble)
            db.session.commit()
            return redirect(url_for('get_immobles'))
        else:
            return "Error en extreure les dades de l'immoble.", 400

    return render_template('afegir_immoble.html')

# Funció per extreure informació d'una URL
def extreure_dades(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Exemple de com extreure dades (ajustar segons la pàgina)
        if "idealista" in url:
            titol = soup.find('span', {'class': 'main-info__title-main'}).text.strip()
            descripcio = soup.find('div', {'class': 'description'}).text.strip()
            preu = soup.find('span', {'class': 'info-data-price'}).text.strip().replace('€', '').replace('.', '')
            ubicacio = soup.find('span', {'class': 'main-info__title-minor'}).text.strip()
        elif "habitaclia" in url:
            titol = soup.find('h1', {'class': 'detail-title'}).text.strip()
            descripcio = soup.find('div', {'class': 'description-body'}).text.strip()
            preu = soup.find('span', {'class': 'price'}).text.strip().replace('€', '').replace('.', '')
            ubicacio = soup.find('span', {'class': 'address'}).text.strip()
        else:
            return None

        return {
            'titol': titol,
            'descripcio': descripcio,
            'preu': int(preu),
            'ubicacio': ubicacio
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

# Ruta per mostrar immobles
@app.route('/immobles', methods=['GET'])
def get_immobles():
    immobles = Immoble.query.all()
    return render_template('immobles.html', immobles=immobles)

if __name__ == '__main__':
    app.run(debug=True)
