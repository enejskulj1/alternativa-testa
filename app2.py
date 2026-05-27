from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tinydb import TinyDB, Query
import os
from werkzeug.utils import secure_filename

# Nastavitev Flask aplikacije in map z viri za socialno deljenje.
app = Flask(__name__, template_folder="templates2", static_folder="static2")
app.secret_key = 'your_secret_key_here'

# Nastavitev baze: ustvari mapo in odpri TinyDB datoteke za uporabnike in objave.
db2_dir = 'db2'
if not os.path.exists(db2_dir):
    os.makedirs(db2_dir)
users_db = TinyDB(os.path.join(db2_dir, 'users.json'))
posts_db = TinyDB(os.path.join(db2_dir, 'posts.json'))

# Nastavi mapo za nalaganje slik objav.
UPLOAD_FOLDER = 'static2/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """Domača ruta: zahteva prijavo in prikaže vse objave."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    posts = posts_db.all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login ruta: preveri uporabniške poverilnice in vzpostavi sejo."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_db.search((Query().username == username) & (Query().password == password))
        if user:
            session['user_id'] = user[0].doc_id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registracijska ruta: dodaj novega uporabnika, če je uporabniško ime prosto."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_db.search(Query().username == username):
            return render_template('register.html', error='Username already exists')
        users_db.insert({'username': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout ruta: počisti sejo in preusmeri na prijavo."""
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_post', methods=['POST'])
def add_post():
    """API klic: ustvari novo objavo z opcijskim nalaganjem slike."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    text = request.form['text']
    image = request.files.get('image')
    image_path = None
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_path = f'/static/uploads/{filename}'  # relativna pot za prikaz v predlogi
    user_id = session['user_id']
    user = users_db.get(doc_id=user_id)
    username = user['username']
    posts_db.insert({'user_id': user_id, 'username': username, 'text': text, 'image': image_path})
    return jsonify({'success': True})

if __name__ == '__main__':
    # Zaženi socialno aplikacijo na portu 5001 v debug načinu.
    app.run(debug=True, port=5001)
