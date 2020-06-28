import json
import requests
import time

class Game():
    def __init__(self, host, player_name, game_id=None):
        self.server = host
        self.player = player_name
        if game_id:
            self.game_id = game_id
            self.status = self.join_game()
        else:
            self.game_id = self.create_game()

    def get_all_games(self):
        result = json.loads(requests.get('http://' + self.server + '/api/all').text)
        return result

    def create_game(self):
        result = json.loads(requests.get('http://' + self.server + '/api/new', params={'player_name': self.player}).text)
        if result['status'] == 'failed':
            raise ValueError(f'Bad response: {result}')
        return result['room']

    def join_game(self):
        result = json.loads(requests.get('http://' + self.server + f'/api/room/{self.game_id}/join/{self.player}').text)
        if result['status'] == 'failed':
            raise ValueError(f'Bad response: {result}')
        return result

    def get_game_status(self):
        result = json.loads(requests.get('http://' + self.server + f'/api/room/{self.game_id}/status').text)
        if result['status'] == 'failed':
            raise ValueError(f'Bad response: {result}')
        return result['result']['status']

    def get_game_state(self):
        result = json.loads(requests.get('http://' + self.server + f'/api/room/{self.game_id}/status').text)
        if result['status'] == 'failed':
            raise ValueError(f'Bad response: {result}')
        return result['result']

    def move(self):
        valid_input = False
        while not valid_input:
            try:
                next_move = input('Enter a move (x, y, vector): ')
                x, y, vector = next_move.split(',')
                resp = requests.post('http://' + self.server + f'/api/room/{self.game_id}/move', 
                json={'player': self.player, 'move': {'x': int(x), 'y': int(y), 'vector': vector}})
                result = json.loads(resp.text)
                if result['status'] == 'failed':
                    raise ValueError(result['message'])
                valid_input = True
            except ValueError as e:
                print(f'Invalid input! {e}')
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
    game_id = input('Enter a game to join [Blank to create a new game]: ')
    game = Game(server, name, game_id=game_id)
    if not game.get_game_status() == 'In progress':
        print(f'Game {game.game_id} created.')
        print('Waiting for other player to join...')
        while not game.get_game_status() == 'In progress': time.sleep(3)
    while game.get_game_status() == 'In progress':
        state = game.get_game_state()
        current_player_turn = state['turn']
        game_status = state['status']
        if not current_player_turn == name:
            print('Waiting for other player to move...')
            while not current_player_turn == name and game_status == 'In progress':
                time.sleep(3)
                state = game.get_game_state()
                current_player_turn = state['turn']
                game_status = state['status']
        print_board(game.get_game_state()['board'])   
        if game_status == 'In progress':
            result = game.move()
        print(result)
    print(game.get_game_status())
