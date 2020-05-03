import json
import requests
import time

def get_all_games(server):
    return json.loads(requests.get('http://' + server + '/api/all').text)

def create_game(server, player):
    return json.loads(requests.get('http://' + server + '/api/new', params={'player': player}).text)

def join_game(server, room, player):
    return json.loads(requests.get('http://' + server + f'/room/{room}/join/{player}').text)

def game_status(server, room):
    return json.loads(requests.get('http://' + server + f'/room/{room}').text)

def move(server, room, player, move):
    return json.loads(requests.post('http://' + server + f'/room/{room}/move', json={'player': player, 'move': move}).text)

def print_board(board):
    output = ''
    for y in board:
        line1 = ''
        line2 = ''
        for x in y:
            if x.x_vector:
                line1 += '. _ '
            else:
                line1 += '.   '
            if x.y_vector:
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
        game_lookup = join_game(server, game, name)
    else:
        game_lookup = create_game(server, name)
    instance = game_lookup['instance']
    if not instance.started:
        print('Waiting for other player to join...')
        while not instance.started:
            time.sleep(10)
            instance = game_status(server, game)
    move = input('Enter a move [Blank to create a new game]: ')