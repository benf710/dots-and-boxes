from flask import Flask, redirect, request, make_response, url_for, render_template
import random
from game import Game, Player

app = Flask(__name__)

games = {}  # {123: <Game object>,...}


@app.route('/', methods=['GET'])
def index():
    return render_template('base.html')

@app.route('/test', methods=['GET'])
def board_test():
    return render_template('board_test.html')

@app.route('/api/all', methods=['GET'])
def get_all():
    output = {}
    for game_id, game in games.items():
        output[game_id] = game.to_dict()
    return output


@app.route('/api/new', methods=['GET'])
def new_game():
    player_name = request.args.get('player_name')
    if not player_name:
        return make_response({'status': 'failed', 'result': 'Missing player parameter.'}, 400)
    room_id = random.randrange(100000)
    while room_id in games.keys():
        room_id = random.randrange(100000)
    return redirect(url_for('join_game', room_id=room_id, player_name=player_name))


@app.route('/api/room/<int:room_id>/join/<player_name>', methods=['GET'])
def join_game(room_id, player_name):
    game_lookup = games.get(room_id)
    if not game_lookup:
        games[room_id] = Game(player1=Player(player_name))
    else:
        game = game_lookup
        if not game.started:
            if player_name != game.player1.name:
                game.player2 = Player(player_name)
                game.start_async()
        else:
            return make_response({'status': 'failed', 'result': 'Two players already joined.'}, 400)
    return redirect(url_for('room_status', room_id=room_id))


@app.route('/api/room/<int:room_id>/status', methods=['GET'])
def room_status(room_id):
    game_lookup = games.get(room_id)
    if not game_lookup:
        resp = ({'status': 'failed', 'room': room_id, 'result': 'Game does not exist.'}, 404)
    else:
        resp = ({'status': 'success', 'room': room_id, 'result': game_lookup.to_dict()}, 200)
    response_obj = make_response(*resp)
    response_obj.headers['Content-Type'] = 'application/json'
    return response_obj


@app.route('/api/room/<int:room_id>/move', methods=['POST'])
def room_move(room_id):
    game_lookup = games.get(room_id)
    data = request.json
    player_name = data.get('player')
    move = data.get('move')  # { 'x': 2, 'y': 3, 'vector': 'x'}
    if not game_lookup:
        return make_response({'status': 'failed', 'result': 'Game not initialized'}, 400)
    else:
        if not (player_name and move):
            return make_response({'status': 'failed', 'result': f'Missing player or move parameter for object: {data}'},
                                 400)
        result = game_lookup.make_move(player_name, move)
        code = 400 if result['status'] == 'failed' else 200
        return make_response(result, code)


if __name__ == '__main__':
    app.run()
