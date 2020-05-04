import json
import requests
import time

def get_all_games(server):
    result = json.loads(requests.get('http://' + server + '/api/all').text)
    return result

def create_game(server, player):
    result = json.loads(requests.get('http://' + server + '/api/new', params={'player_name': player}).text)
    if result['status'] == 'failed':
        raise ValueError(f'Bad response: {result}')
    return result

def join_game(server, room, player):
    result = json.loads(requests.get('http://' + server + f'/api/room/{room}/join/{player}').text)
    if result['status'] == 'failed':
        raise ValueError(f'Bad response: {result}')
    return result

def get_game_status(server, room):
    result = json.loads(requests.get('http://' + server + f'/api/room/{room}/status').text)
    if result['status'] == 'failed':
        raise ValueError(f'Bad response: {result}')
    return result

def move(server, room, player, move):
    result = json.loads(requests.post('http://' + server + f'/api/room/{room}/move', json={'player': player, 'move': move}).text)
    if result['status'] == 'failed':
        raise ValueError(f'Bad response: {result}')
    return result

def print_board(board):
    output = ''
    for y in board:
        line1 = ''
        line2 = ''
        for x in y:
            if x['x_vector']:
                line1 += '. _ '
            else:
                line1 += '.   '
            if x['y_vector']:
                line2 += '|   '
            else:
                line2 += '    '
        output += line1 + '\n' + line2 + '\n'
    print(output)

if __name__ == '__main__':
    server = '127.0.0.1:5000'
    name = ''
    while name.strip() == '':
        name = input('Enter you player name: ')
    game = input('Enter a game to join [Blank to create a new game]: ')
    if game:
        status = join_game(server, game, name)['result']['status']
    else:
        game = create_game(server, name)['room']
        status = 'Waiting for another player to join...'
    print(get_game_status(server, game))
    if not status == 'In progress':
        print('Waiting for other player to join...')
        while not status == 'In progress':
            time.sleep(3)
            status = get_game_status(server, game)['result']['status']
    while get_game_status(server, game)['result']['status'] == 'In progress':
        result = get_game_status(server, game)['result']
        current_player_turn = result['turn']
        game_status = result['status']
        if not current_player_turn == name:
            print('Waiting for other player to move...')
            while not current_player_turn == name and game_status == 'In progress':
                time.sleep(3)
                result = get_game_status(server, game)['result']
                current_player_turn = result['turn']
                game_status = result['status']
        print_board(get_game_status(server, game)['result']['board'])
        next_move = input('Enter a move [Blank to create a new game]: ')
        x, y, vector = next_move.split(',')
        print(move(server, game, name, {'x': int(x), 'y': int(y), 'vector': vector}))
    print(get_game_status(server, game))