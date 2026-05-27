from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import os

# Nastavitev Flask aplikacije za upravljanje opravil.
app = Flask(__name__, template_folder="templates3", static_folder="static3")

# Nastavitev baze: ustvari mapo za shranjevanje in odpri JSON datoteko.
db3_dir = 'db3'
if not os.path.exists(db3_dir):
    os.makedirs(db3_dir)
tasks_db = TinyDB(os.path.join(db3_dir, 'tasks.json'))

@app.route('/')
def index():
    """Domača ruta: prikaže vsa trenutna opravila."""
    tasks = tasks_db.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    """API klic: vstavi novo opravilo v bazo."""
    title = request.form['title']
    description = request.form['description']
    status = request.form['status']
    tasks_db.insert({'title': title, 'description': description, 'status': status})
    return jsonify({'success': True})

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    """API klic: posodobi obstoječe opravilo po ID-ju."""
    task = tasks_db.get(doc_id=task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    title = request.form['title']
    description = request.form['description']
    status = request.form['status']
    tasks_db.update({'title': title, 'description': description, 'status': status}, doc_ids=[task_id])
    return jsonify({'success': True})

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """API klic: odstrani opravilo po ID-ju."""
    task = tasks_db.get(doc_id=task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    tasks_db.remove(doc_ids=[task_id])
    return jsonify({'success': True})

if __name__ == '__main__':
    # Zaženi aplikacijo za upravljanje opravil na portu 5002 v debug načinu.
    app.run(debug=True, port=5002)
