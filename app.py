from flask import Flask, request, jsonify, render_template
from game import CoupGame

app = Flask(__name__)
game = CoupGame()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start():
    data = request.json
    players = data['players']
    game.start_game(players)
    return jsonify({"players": players, "game_state": game.get_status()})

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    player = data['player']
    move = data['move']
    result = game.make_move(player, move)
    return jsonify({"result": result, "current_player": game.get_current_player()})


@app.route('/restart', methods=['POST'])
def restart():
    game.start_game(game.players)
    return jsonify({"game_state": game.get_status()})


if __name__ == '__main__':
    app.run(debug=True)
