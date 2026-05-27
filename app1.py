from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tinydb import TinyDB, Query
import os

# Nastavitev Flask aplikacije in predlog/static map.
app = Flask(__name__, template_folder="templates1", static_folder="static1")
app.secret_key = 'your_secret_key_here'  # Zavaruj piškotke seje za stanje prijave.

# Nastavitev baze: ustvari mapo in odpri TinyDB JSON datoteke.
db_dir = 'db'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
users_db = TinyDB(os.path.join(db_dir, 'users.json'))
notes_db = TinyDB(os.path.join(db_dir, 'notes.json'))

@app.route('/')
def index():
    """Domača stran: prikaže opombe prijavljenega uporabnika."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    notes = notes_db.search(Query().user_id == user_id)
    return render_template('index.html', notes=notes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login ruta: prikaže formo pri GET in preveri poverilnice pri POST."""
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
    """Registracijska ruta: ustvari novega uporabnika, če uporabniško ime še ne obstaja."""
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

@app.route('/add_note', methods=['POST'])
def add_note():
    """API klic: dodaj novo opombo za prijavljenega uporabnika."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    title = request.form['title']
    content = request.form['content']
    user_id = session['user_id']
    notes_db.insert({'user_id': user_id, 'title': title, 'content': content})
    return jsonify({'success': True})

@app.route('/edit_note/<int:note_id>', methods=['POST'])
def edit_note(note_id):
    """API klic: posodobi obstoječo opombo po preverjanju lastništva."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session['user_id']
    note = notes_db.get(doc_id=note_id)
    if not note or note['user_id'] != user_id:
        return jsonify({'error': 'Note not found'}), 404
    title = request.form['title']
    content = request.form['content']
    notes_db.update({'title': title, 'content': content}, doc_ids=[note_id])
    return jsonify({'success': True})

@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    """API klic: izbriši opombo, ki pripada trenutnemu uporabniku."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session['user_id']
    note = notes_db.get(doc_id=note_id)
    if not note or note['user_id'] != user_id:
        return jsonify({'error': 'Note not found'}), 404
    notes_db.remove(doc_ids=[note_id])
    return jsonify({'success': True})

if __name__ == '__main__':
    # Zaženi aplikacijo za osebne zapiske na portu 5000 v debug načinu.
    app.run(debug=True, port=5000)
