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
def scraping():  # Nom canviat de `scraping_page` a `scraping`
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


