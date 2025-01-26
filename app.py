import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from api.scraping import extreure_dades_immobles

# Carregar variables d'entorn..
load_dotenv()

database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model de la base de dades.
class Immoble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adreca = db.Column(db.String(200), nullable=False)
    ciutat = db.Column(db.String(100), nullable=False)
    preu = db.Column(db.Float, nullable=False)
    superficie = db.Column(db.Float, nullable=False)
    habitacions = db.Column(db.Integer, nullable=False)
    estat_reforma = db.Column(db.String(100), nullable=True)
    fotos = db.Column(db.Text, nullable=True)  # Emmagatzema URLs de fotos separades per comes
    cost_reforma_estim = db.Column(db.Float, nullable=True)
    preu_objectiu = db.Column(db.Float, nullable=True)
    estat_ocupacional = db.Column(db.String(100), nullable=True)
    informacio_urbanistica = db.Column(db.Text, nullable=True)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)

# Serializer
class ImmobleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Immoble

immoble_schema = ImmobleSchema()
immobles_schema = ImmobleSchema(many=True)

# Rutes principals
@app.route('/')
def index():
    return render_template('index.html')

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

# Rutes de l'API
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
        nou_immoble = Immoble(
            adreca=dades['adreca'],
            ciutat=dades['ciutat'],
            preu=dades['preu'],
            superficie=dades['superficie'],
            habitacions=dades['habitacions'],
            estat_reforma=dades.get('estat_reforma'),
            fotos=dades.get('fotos'),
            cost_reforma_estim=dades.get('cost_reforma_estim'),
            preu_objectiu=dades.get('preu_objectiu'),
            estat_ocupacional=dades.get('estat_ocupacional'),
            informacio_urbanistica=dades.get('informacio_urbanistica'),
            latitud=dades.get('latitud'),
            longitud=dades.get('longitud')
        )
        db.session.add(nou_immoble)
        db.session.commit()
        return jsonify(immoble_schema.dump(nou_immoble)), 201
    except Exception as e:
        return jsonify({'error': f"Error al crear l'immoble: {str(e)}"}), 400

@app.route('/api/immobles/<int:id>', methods=['PUT'])
def actualitzar_immoble(id):
    immoble = Immoble.query.get_or_404(id)
    dades = request.json
    try:
        immoble.adreca = dades.get('adreca', immoble.adreca)
        immoble.ciutat = dades.get('ciutat', immoble.ciutat)
        immoble.preu = dades.get('preu', immoble.preu)
        immoble.superficie = dades.get('superficie', immoble.superficie)
        immoble.habitacions = dades.get('habitacions', immoble.habitacions)
        immoble.estat_reforma = dades.get('estat_reforma', immoble.estat_reforma)
        immoble.fotos = dades.get('fotos', immoble.fotos)
        immoble.cost_reforma_estim = dades.get('cost_reforma_estim', immoble.cost_reforma_estim)
        immoble.preu_objectiu = dades.get('preu_objectiu', immoble.preu_objectiu)
        immoble.estat_ocupacional = dades.get('estat_ocupacional', immoble.estat_ocupacional)
        immoble.informacio_urbanistica = dades.get('informacio_urbanistica', immoble.informacio_urbanistica)
        immoble.latitud = dades.get('latitud', immoble.latitud)
        immoble.longitud = dades.get('longitud', immoble.longitud)

        db.session.commit()
        return jsonify(immoble_schema.dump(immoble))
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

@app.route('/api/scraping', methods=['POST'])
def scraping_immobles():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'Cal proporcionar una URL'}), 400

    try:
        dades_immobles = extreure_dades_immobles(url)

        if not dades_immobles:
            return jsonify({'error': 'No s\'han trobat immobles a la URL proporcionada.'}), 404

        for dades in dades_immobles:
            nou_immoble = Immoble(
                adreca=dades['adreca'],
                ciutat=dades['ciutat'],
                preu=dades['preu'],
                superficie=dades['superficie'],
                habitacions=dades['habitacions']
            )
            db.session.add(nou_immoble)
        db.session.commit()

        return jsonify({'missatge': 'Dades extretes i afegides correctament'}), 201
    except Exception as e:
        return jsonify({'error': f"Error durant el scraping: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

