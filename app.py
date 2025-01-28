import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from api.scraping_idealista import ScraperIdealista
# Si s'implementen altres portals en el futur
# from api.scraping_fotocasa import ScraperFotocasa

# Carregar variables d'entorn
load_dotenv()

# Configuració de l'aplicació
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialitzar extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Models de la base de dades
class Immoble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titol = db.Column(db.String(200), nullable=True)
    adreca = db.Column(db.String(200), nullable=True)
    ciutat = db.Column(db.String(100), nullable=True)
    preu = db.Column(db.Float, nullable=True)
    superficie = db.Column(db.Float, nullable=True)
    habitacions = db.Column(db.Integer, nullable=True)
    banys = db.Column(db.Integer, nullable=True)
    estat_conservacio = db.Column(db.String(100), nullable=True)
    caracteristiques = db.Column(db.Text, nullable=True)
    certificat_energia = db.Column(db.String(20), nullable=True)
    terrassa = db.Column(db.Boolean, default=False)
    piscina = db.Column(db.Boolean, default=False)
    aire_condicionat = db.Column(db.Boolean, default=False)
    parking = db.Column(db.Boolean, default=False)
    descripcio = db.Column(db.Text, nullable=True)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    portal = db.Column(db.String(50), nullable=False)


# Serializer
class ImmobleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Immoble


immoble_schema = ImmobleSchema()
immobles_schema = ImmobleSchema(many=True)


# Helpers
def create_or_update_immoble(dades, portal, immoble=None):
    """
    Crea o actualitza un objecte Immoble amb les dades proporcionades.
    """
    try:
        if immoble is None:
            immoble = Immoble()

        immoble.titol = dades.get('títol', immoble.titol)
        immoble.adreca = dades.get('adreca', immoble.adreca)
        immoble.ciutat = dades.get('ciutat', immoble.ciutat)
        immoble.preu = dades.get('preu', immoble.preu)
        immoble.superficie = dades.get('superficie_construida', immoble.superficie)
        immoble.habitacions = dades.get('habitacions', immoble.habitacions)
        immoble.banys = dades.get('banys', immoble.banys)
        immoble.estat_conservacio = dades.get('estat_conservacio', immoble.estat_conservacio)
        immoble.caracteristiques = "; ".join(dades.get('caracteristiques', immoble.caracteristiques.split("; ")))
        immoble.certificat_energia = dades.get('certificat_energia', immoble.certificat_energia)
        immoble.terrassa = dades.get('terrassa', immoble.terrassa) == "Sí"
        immoble.piscina = dades.get('piscina', immoble.piscina) == "Sí"
        immoble.aire_condicionat = dades.get('aire_condicionat', immoble.aire_condicionat) == "Sí"
        immoble.parking = dades.get('parking', immoble.parking) == "Inclòs"
        immoble.descripcio = dades.get('descripcio', immoble.descripcio)
        immoble.portal = portal
        return immoble
    except Exception as e:
        raise ValueError(f"Error al processar les dades de l'immoble: {e}")


# Rutes principals
@app.route('/')
def index():
    """
    Pàgina principal.
    """
    return render_template('index.html', missatge="Benvingut al gestor d'immobles!")


@app.route('/afegir')
def afegir_immoble():
    """
    Pàgina per afegir immobles manualment.
    """
    return render_template('afegir_immoble.html')


@app.route('/llistat')
def llistar_immobles():
    """
    Pàgina per llistar els immobles desats.
    """
    return render_template('llistar_immobles.html')


@app.route('/scraping')
def scraping():
    """
    Pàgina per fer scraping de portals immobiliaris.
    """
    return render_template('scraping.html')


# API: Scraping
@app.route('/api/scraping', methods=['POST'])
def scraping_immobles():
    """
    Ruta d'API per fer scraping.
    """
    url = request.json.get('url')
    portal = request.json.get('portal')
    if not url or not portal:
        return jsonify({'error': 'Cal proporcionar una URL i un portal'}), 400

    try:
        # Seleccionar scraper segons el portal
        if portal.lower() == 'idealista':
            scraper = ScraperIdealista(api_key=os.getenv("SCRAPER_API_KEY"))
        # Si s'implementen més portals:
        # elif portal.lower() == 'fotocasa':
        #     scraper = ScraperFotocasa(api_key=os.getenv("SCRAPER_API_KEY"))
        else:
            return jsonify({'error': f"Portal {portal} no suportat."}), 400

        # Executar scraping
        dades = scraper.extreu_dades(url)
        if not dades:
            return jsonify({'error': 'No s\'han trobat dades.'}), 404

        # Crear i guardar l'immoble
        nou_immoble = create_or_update_immoble(dades, portal)
        db.session.add(nou_immoble)
        db.session.commit()

        return jsonify({'missatge': 'Dades extretes correctament', 'immoble': immoble_schema.dump(nou_immoble)}), 201
    except Exception as e:
        return jsonify({'error': f"Error durant el scraping: {str(e)}"}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

