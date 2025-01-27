import os
import asyncio
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from api.scraping import extreure_dades_immobles, extreure_dades_immoble_detall

# Carregar variables d'entorn
load_dotenv()

# Configurar la base de dades........
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model de la base de dades
class Immoble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adreca = db.Column(db.String(200), nullable=True)
    ciutat = db.Column(db.String(100), nullable=True)
    preu = db.Column(db.Float, nullable=True)
    superficie = db.Column(db.Float, nullable=True)
    habitacions = db.Column(db.Integer, nullable=True)
    estat_reforma = db.Column(db.String(100), nullable=True)
    fotos = db.Column(db.Text, nullable=True)  # URLs separades per comes
    cost_reforma_estim = db.Column(db.Float, nullable=True)
    preu_objectiu = db.Column(db.Float, nullable=True)
    estat_ocupacional = db.Column(db.String(100), nullable=True)
    informacio_urbanistica = db.Column(db.Text, nullable=True)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    tipus = db.Column(db.String(100), nullable=True)
    certificat_energia = db.Column(db.String(10), nullable=True)
    titol = db.Column(db.String(200), nullable=True)
    caracteristiques = db.Column(db.Text, nullable=True)

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
            adreca=dades.get('adreca'),
            ciutat=dades.get('ciutat'),
            preu=dades.get('preu'),
            superficie=dades.get('superficie'),
            habitacions=dades.get('habitacions'),
            estat_reforma=dades.get('estat_reforma'),
            fotos=dades.get('fotos'),
            cost_reforma_estim=dades.get('cost_reforma_estim'),
            preu_objectiu=dades.get('preu_objectiu'),
            estat_ocupacional=dades.get('estat_ocupacional'),
            informacio_urbanistica=dades.get('informacio_urbanistica'),
            latitud=dades.get('latitud'),
            longitud=dades.get('longitud'),
            tipus=dades.get('tipus'),
            certificat_energia=dades.get('certificat_energia'),
            titol=dades.get('titol'),
            caracteristiques="; ".join(dades.get('caracteristiques', []))
        )
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if "fotocasa" in url and "/d?" in url:
            dades_immoble = loop.run_until_complete(extreure_dades_immoble_detall(url))
            if not dades_immoble:
                return jsonify({'error': 'No s\'han pogut extreure dades de la URL proporcionada.'}), 404

            nou_immoble = Immoble(
                titol=dades_immoble.get('titol'),
                ciutat=dades_immoble.get('ubicacio'),
                preu=dades_immoble.get('preu'),
                caracteristiques="; ".join(dades_immoble.get('caracteristiques', []))
            )
            db.session.add(nou_immoble)
            db.session.commit()

            return jsonify({'missatge': 'Dades extretes i afegides correctament', 'immoble': immoble_schema.dump(nou_immoble)}), 201

        else:
            dades_immobles = loop.run_until_complete(extreure_dades_immobles(url))
            if not dades_immobles:
                return jsonify({'error': 'No s\'han trobat immobles a la URL proporcionada.'}), 404

            for dades in dades_immobles:
                nou_immoble = Immoble(
                    titol=dades['titol'],
                    ciutat=dades.get('ubicacio', ''),
                    preu=dades.get('preu', 0),
                    caracteristiques="; ".join(dades.get('caracteristiques', []))
                )
                db.session.add(nou_immoble)
            db.session.commit()

            return jsonify({'missatge': 'Dades extretes i afegides correctament'}), 201

    except Exception as e:
        return jsonify({'error': f"Error durant el scraping: {str(e)}"}), 500

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
        immoble.tipus = dades.get('tipus', immoble.tipus)
        immoble.certificat_energia = dades.get('certificat_energia', immoble.certificat_energia)
        immoble.titol = dades.get('titol', immoble.titol)
        immoble.caracteristiques = "; ".join(dades.get('caracteristiques', immoble.caracteristiques.split("; ")))

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


