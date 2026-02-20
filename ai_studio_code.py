from flask import Flask, render_template, jsonify
import random
from faker import Faker

app = Flask(__name__)
fake = Faker()

# Configuration
GRID_SIZE = 9
PLAYER_COUNT = 20

def generate_players():
    players = []
    for i in range(PLAYER_COUNT):
        players.append({
            "id": i,
            "name": fake.name(),
            "age": random.randint(18, 65),
            "x": random.randint(0, GRID_SIZE - 1),
            "y": random.randint(0, GRID_SIZE - 1),
            "color": f"hsl({random.randint(0, 360)}, 70%, 60%)"
        })
    return players

@app.route('/')
def index():
    return render_template('index.html', grid_size=GRID_SIZE)

@app.route('/api/players')
def get_players():
    return jsonify(generate_players())

if __name__ == '__main__':
    app.run(debug=True)