from flask import Flask, redirect, request, make_response, url_for, render_template
import random
from game import Game, Player

app = Flask(__name__)

games = {} # {123: {'status': 'Waiting for player', 'instance': <Game object>}}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', games=list(games.keys()))

@app.route('/api/all', methods=['GET'])
def all():
    return {'games': games}

@app.route('/api/new', methods=['GET'])
def new_game():
    player = request.args.get('player')
    if not player:
        return make_response({'status': 'failed', 'result': 'Missing player parameter.'}, 400)
    room_id = random.randrange(100000)
    while room_id in games.keys():
        room_id = random.randrange(100000)
    return redirect(url_for('join_game', room_id=room_id, player=player))

@app.route('/api/room/<int:room_id>/join/<player_name>', methods=['GET'])
def join_game(room_id, player_name):
    game_lookup = games.get(room_id)
    if not game_lookup:
        games[room_id] = {'status': 'Waiting for another player to join.', 'instance': Game(player1=Player(player_name))}
    else:
        game = game_lookup['instance']
        if not game.started:
            if player_name != game.player1.name:
                game.player2 = Player(player_name)
                game.start_async()
                game_lookup['status'] = 'Game started.'
        else:
            return make_response({'status': 'failed', 'result': 'Two players already joined.'}, 400)
    return redirect(url_for('room_status', room_id=room_id))

@app.route('/api/room/<int:room_id>/status', methods=['GET'])
def room_status(room_id):
    game_lookup = games.get(room_id)
    if not game_lookup:
        resp = ({'status': 'failed', 'result': 'Game does not exist.'}, 404)
    else:
        resp = ({'status': 'success', 'result': game_lookup}, 200)
    response_obj = make_response(*resp)
    response_obj.headers['Content-Type'] = 'application/json'
    return response_obj

@app.route('/api/room/<int:room_id>/move', methods=['POST'])
def room_move(room_id):
    game_lookup = games.get(room_id)
    data = request.json
    player_name = data.get('player')
    move = data.get('move') # { 'x': 2, 'y': 3, 'vector': 'x'}
    if not game_lookup:
        return make_response({'status': 'failed', 'result': 'Game not initialized'}, 400)
    else:
        game = game_lookup['instance']
        if not (player_name and move):
            return make_response({'status': 'failed', 'result': f'Missing player or move parameter for object: {data}'}, 400)
        result = game.make_move(player_name, move)
        if result['status'] == 'failed':
            return make_response({'status': 'failed', 'result': result}, 400)
        else:
            return redirect(url_for('room_status', room_id=room_id))

if __name__ == '__main__':
    app.run()