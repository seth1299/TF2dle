from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('TF2_weapons.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route that renders the HTML page for the game
@app.route('/')
def index():
    return render_template('index.html')

# API route to fetch all weapons from the database
@app.route('/api/weapons', methods=['GET'])
def get_weapons():
    conn = get_db_connection()
    weapons = conn.execute('SELECT name, class, slot, ammo FROM weapons').fetchall()
    conn.close()

    weapon_list = [{'name': weapon['name'], 'class': weapon['class'], 'slot': weapon['slot'], 'ammo': weapon['ammo']} for weapon in weapons]
    return jsonify(weapon_list)

# API route to fetch a specific weapon by name
@app.route('/api/weapons/<name>', methods=['GET'])
def get_weapon_by_name(name):
    conn = get_db_connection()
    weapon = conn.execute('SELECT name, class, slot, ammo FROM weapons WHERE name = ?', (name,)).fetchone()
    conn.close()

    if weapon is None:
        return jsonify({'error': 'Weapon not found'}), 404

    weapon_data = {'name': weapon['name'], 'class': weapon['class'], 'slot': weapon['slot']}
    return jsonify(weapon_data)

# API route to handle guessing a weapon (can be expanded based on game logic)
@app.route('/api/guess', methods=['POST'])
def guess_weapon():
    data = request.json
    guess_name = data.get('name')

    conn = get_db_connection()
    weapon = conn.execute('SELECT name FROM weapons WHERE name = ?', (guess_name,)).fetchone()
    conn.close()

    if weapon:
        return jsonify({'message': 'Correct guess!', 'weapon': guess_name})
    else:
        return jsonify({'message': 'Incorrect guess, try again!'}), 404

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
