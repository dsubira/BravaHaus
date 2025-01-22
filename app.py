from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuració de la base de dades (substitueix amb DATABASE_URL real)..
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ua1opglmi2dcvp:pb2846a65596ce3eaf1efe7be5ed91d369e1af83651c418d3a77c28920640634b@cah8ha8ra8h8i7.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d34184f0va5qsb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Exemple de model (immobles)
class Immoble(db.Model):
    __tablename__ = 'immobles'
    id = db.Column(db.Integer, primary_key=True)
    titol = db.Column(db.String(255), nullable=False)
    descripcio = db.Column(db.Text)
    preu = db.Column(db.Numeric, nullable=False)
    ubicacio = db.Column(db.String(255))

# Ruta principal
@app.route('/')
def home():
    return "Benvingut a BravaHaus!"

# Ruta per consultar immobles
@app.route('/immobles', methods=['GET'])
def get_immobles():
    immobles = Immoble.query.all()
    return jsonify([{
        'id': i.id,
        'titol': i.titol,
        'preu': float(i.preu),
        'ubicacio': i.ubicacio
    } for i in immobles])

# Ruta per afegir immobles
@app.route('/immobles', methods=['POST'])
def add_immoble():
    data = request.get_json()
    nou_immoble = Immoble(
        titol=data['titol'],
        descripcio=data.get('descripcio', ''),
        preu=data['preu'],
        ubicacio=data['ubicacio']
    )
    db.session.add(nou_immoble)
    db.session.commit()
    return jsonify({'message': 'Immoble afegit correctament!'}), 201

if __name__ == '__main__':
    app.run(debug=True)

