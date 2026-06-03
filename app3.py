from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import os

# Ustvari in konfiguriraj Flask aplikacijo za upravljanje opravil.
# template_folder in static_folder določata mapi za HTML predloge in statične datoteke.
app = Flask(__name__, template_folder="templates3", static_folder="static3")

# Določi imenik baze podatkov in poskrbi, da obstaja pred odpiranjem datoteke.
# TinyDB shrani zapise v JSON datoteko, zato opravila hranimo v db3/tasks.json.
db3_dir = 'db3'
if not os.path.exists(db3_dir):
    os.makedirs(db3_dir)

# Odpri datoteko TinyDB baze; ta objekt se uporablja za vse CRUD operacije opravil.
tasks_db = TinyDB(os.path.join(db3_dir, 'tasks.json'))

@app.route('/')
def index():
    """Glavna pot: izriše glavno stran s seznamom vseh shranjenih opravil."""
    # Naloži vsa opravila iz baze in pridobi seznam slovarjev opravil.
    tasks = tasks_db.all()

    # Prikaži predlogo index.html in ji posreduj seznam opravil.
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    """Pot za dodajanje opravil: vstavi novo opravilo v TinyDB bazo."""
    # Preberi polja iz poslanega obrazca v telesu zahteve.
    title = request.form['title']
    description = request.form['description']
    status = request.form['status']

    # Vstavi nov zapis opravila v TinyDB bazo.
    tasks_db.insert({'title': title, 'description': description, 'status': status})

    # Vrni JSON odgovor, ki označuje uspeh.
    return jsonify({'success': True})

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    """Pot za urejanje opravil: posodobi obstoječe opravilo po ID-ju dokumenta."""
    # Pridobi opravilo po TinyDB dokumentnem ID-ju, da preveriš njegovo obstojnost.
    task = tasks_db.get(doc_id=task_id)
    if not task:
        # Če opravilo ne obstaja, vrni JSON napako s statusom 404.
        return jsonify({'error': 'Task not found'}), 404

    # Preberi posodobljene vrednosti iz podatkov obrazca.
    title = request.form['title']
    description = request.form['description']
    status = request.form['status']

    # Posodobi zapis opravila v TinyDB z novimi vrednostmi.
    tasks_db.update({'title': title, 'description': description, 'status': status}, doc_ids=[task_id])

    # Pošlji potrditev uspešne posodobitve nazaj odjemalcu.
    return jsonify({'success': True})

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """Pot za brisanje opravil: odstrani opravilo iz baze po ID-ju."""
    # Preveri, ali opravilo obstaja, preden ga poskusiš izbrisati.
    task = tasks_db.get(doc_id=task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # Odstri zapis opravila iz baze podatkov.
    tasks_db.remove(doc_ids=[task_id])

    # Vrni odgovor o uspešnem brisanju.
    return jsonify({'success': True})

if __name__ == '__main__':
    # Zaženi razvojni strežnik Flask na portu 5002 z vključenim načinom debug.
    # Debug način je koristen med razvojem, ker ponovno naloži kodo ob spremembi.
    app.run(debug=True, port=5002)
