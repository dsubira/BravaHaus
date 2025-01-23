from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuració de la base de dades.
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
    return render_template('index.html')

# Ruta per consultar immobles
@app.route('/immobles', methods=['GET'])
def get_immobles():
    immobles = Immoble.query.all()
    return render_template('immobles.html', immobles=immobles)

# Ruta per afegir immobles
@app.route('/afegir-immoble', methods=['GET', 'POST'])
def afegir_immoble():
    if request.method == 'POST':
        titol = request.form.get('titol')
        descripcio = request.form.get('descripcio')
        preu = request.form.get('preu')
        ubicacio = request.form.get('ubicacio')

        nou_immoble = Immoble(
            titol=titol,
            descripcio=descripcio,
            preu=preu,
            ubicacio=ubicacio
        )
        db.session.add(nou_immoble)
        db.session.commit()

        return "Immoble afegit correctament!"
    return render_template('afegir_immoble.html')

if __name__ == '__main__':
    app.run(debug=True)
