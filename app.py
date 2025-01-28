import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from api.scraping_idealista import ScraperIdealista

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
    immoble.caracteristiques = "; ".join(
        dades.get('caracteristiques', "").split("; ")
        if dades.get('caracteristiques') else []
    )
    immoble.certificat_energia = dades.get('certificat_energia', immoble.certificat_energia)
    immoble.terrassa = dades.get('terrassa', immoble.terrassa) == "Sí"
    immoble.piscina = dades.get('piscina', immoble.piscina) == "Sí"
    immoble.aire_condicionat = dades.get('aire_condicionat', immoble.aire_condicionat) == "Sí"
    immoble.parking = dades.get('parking', immoble.parking) == "Inclòs"
    immoble.descripcio = dades.get('descripcio', immoble.descripcio)
    immoble.portal = portal
    return immoble

# Rutes HTML
@app.route('/')
def index():
    return render_template('index.html', missatge="Benvingut al gestor d'immobles!")

@app.route('/afegir')
def afegir_immoble():
    return render_template('afegir_immoble.html')

@app.route('/llistat')
def llistar_immobles():
    immobles = Immoble.query.all()
    return render_template('llistar_immobles.html', immobles=immobles)

@app.route('/scraping')
def scraping():
    return render_template('scraping.html')

@app.route('/detalls/<int:immoble_id>')
def detalls_immoble(immoble_id):
    immoble = Immoble.query.get_or_404(immoble_id)
    return render_template('detalls_immoble.html', immoble=immoble)

# Rutes API
@app.route('/api/immobles', methods=['GET'])
def obtenir_immobles():
    immobles = Immoble.query.all()
    return jsonify(immobles_schema.dump(immobles))

@app.route('/api/immobles/<int:id>', methods=['GET'])
def obtenir_immoble(id):
    immoble = Immoble.query.get_or_404(id)
    return jsonify(immoble_schema.dump(immoble))

@app.route('/api/immobles', methods=['POST'])
def afegir_immoble_api():
    dades = request.json
    try:
        nou_immoble = create_or_update_immoble(dades, portal="Manual")
        db.session.add(nou_immoble)
        db.session.commit()
        return jsonify(immoble_schema.dump(nou_immoble)), 201
    except Exception as e:
        return jsonify({'error': f"Error al crear l'immoble: {str(e)}"}), 400

@app.route('/api/scraping', methods=['POST'])
def scraping_immobles():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'Cal proporcionar una URL'}), 400

    try:
        scraper = ScraperIdealista(api_key=os.getenv("SCRAPER_API_KEY"))
        dades = scraper.extreu_dades(url)
        if not dades:
            return jsonify({'error': 'No s\'han trobat dades.'}), 404

        nou_immoble = create_or_update_immoble(dades, "Idealista")
        db.session.add(nou_immoble)
        db.session.commit()

        return jsonify({'missatge': 'Dades extretes correctament', 'immoble': immoble_schema.dump(nou_immoble)}), 201
    except Exception as e:
        return jsonify({'error': f"Error durant el scraping: {str(e)}"}), 500

@app.route('/api/immobles/<int:id>', methods=['PUT'])
def actualitzar_immoble(id):
    immoble = Immoble.query.get_or_404(id)
    dades = request.json
    try:
        updated_immoble = create_or_update_immoble(dades, immoble.portal, immoble)
        db.session.commit()
        return jsonify(immoble_schema.dump(updated_immoble))
    except Exception as e:
        return jsonify({'error': f"Error al actualitzar l'immoble: {str(e)}"}), 400

@app.route('/api/immobles/<int:id>', methods=['DELETE'])
def eliminar_immoble(id):
    immoble = Immoble.query.get_or_404(id)
    try:
        db.session.delete(immoble)
        db.session.commit()
        return '', 204
    except Exception as e:
        return jsonify({'error': f"Error al eliminar l'immoble: {str(e)}"}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


