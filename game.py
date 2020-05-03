import asyncio
import random
import json

class Game(object):
    def __init__(self, player1=None, player2=None):
        self.player1 = player1
        self.player2 = player2
        self.spectators = []
        self.board = Board()
        self.started = False

    def __str__(self):
        p1 = self.player1
        p2 = self.player2
        if not self.started:
            game_status = 'Not Started'
        elif self.board.filled():
            winning_player = max(p1, p2, key=lambda player: player.score)
            game_status = f'Game over. Winner: {winning_player}'
        else:
            game_status = 'In progress'
        status = json.dumps({'game': game_status, 'board': str(self.board), 'score': {p1.name: p1.score, p2.name: p2.score}, 'turn': p1.name if self.is_player1_turn else p2.name})
        return status

    def start_async(self):
        self.started = True
        self.is_player1_turn = True
    
    def start_sync(self):
        self.started = True
        self.is_player1_turn = True
        print(self.board)
        while not self.board.filled():
            current_player = self.get_current_player()
            x, y, vector = current_player.set_move(self.board)
            completed_boxes = self.board.update(x, y, vector)
            if completed_boxes == 0:
                self.is_player1_turn = not self.is_player1_turn
            else:
                current_player.score += completed_boxes
                print(f"{current_player} scored {completed_boxes} points!")
            print(self.board)
        winning_player = max(self.player1, self.player2, key=lambda player: player.score)
        print(f'Game over.\n{winning_player} wins!\n\n{self.player1} Score: {self.player1.score}\n{self.player2} Score: {self.player2.score}')
    
    def get_current_player(self):
        return self.player1 if self.is_player1_turn else self.player2

    def ready_to_start(self):
        if not self.started:
            if self.player1 and self.player2:
                return True
        return False
    
    def make_move(self, player, move_obj):
        if (player == self.player1) == self.is_player1_turn:
            if self.board.legal_move(move_obj['x'], move_obj['y'], move_obj['vector']):
                completed_boxes = self.board.update(move_obj['x'], move_obj['y'], move_obj['vector'])
                if completed_boxes == 0:
                    self.is_player1_turn = not self.is_player1_turn
                else:
                    if self.is_player1_turn:
                        self.player1.score += completed_boxes
                    else:
                        self.player2.score += completed_boxes
                status = {'status': 'success', 'message': f"You scored {completed_boxes} points!"}
            else:
                status = {'status': 'failed', 'message': f'{player.name}: Illegal move: {move_obj}'}
        else:
            status = {'status': 'failed', 'message': "Not your turn"}
        return status

class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0
    
    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, str):
            return True if self.name == other else False
        else:
            try:
                if self.name == other.name:
                    return True
            except AttributeError:
                pass
        return False
    
    def set_move(self, board):
        while True:
            try:
                move = input(f"{self.name}, enter a dot and vector ex. 0,0,x: ").split(',')
                x, y, vector = move
                x = int(x)
                y = int(y)
                if len(move) != 3: 
                    raise ValueError("Move input did not consist of 3 values")
                if board.legal_move(x, y, vector):
                    return x, y, vector
            except ValueError as e:
                print(f"Invalid input: {move}. {e}")


class Board(object):
    def __init__(self, x=2, y=2):
        self.board = []
        y_v = True
        for y_iter in range(y):
            row = []
            self.board.append(row)
            if y_iter == y - 1:
                y_v = False
            for x_iter in range(x):
                if x_iter == x - 1:
                    x_v = False
                else:
                    x_v = True
                dot = Dot(x_iter, y_iter, x_potential=x_v, y_potential=y_v)
                row.append(dot)
    
    def __str__(self):
        return str(self.board)

    def printable(self):
        output = ''
        for y in self.board:
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
        return output

    def filled(self):
        for row in self.board:
            for dot in row:
                if not (dot.x_potential == dot.x_vector and dot.y_potential == dot.y_vector):
                    return False
        return True
    
    def completed_boxes(self, dot, vector):
        x = dot.x
        y = dot.y
        if vector == 'x':
            if dot.y == 0:
                bc_dot = self.board[y+1][x]
                mr_dot = self.board[y][x+1]
                return 1 if dot.y_vector and bc_dot.x_vector and mr_dot.y_vector else 0
            elif dot.y == len(self.board) - 1:
                tc_dot = self.board[y-1][x]
                tr_dot = self.board[y-1][x+1]
                return 1 if tc_dot.y_vector and tc_dot.x_vector and tr_dot.y_vector else 0
            else:
                count = 0
                bc_dot = self.board[y+1][x]
                tc_dot = self.board[y-1][x]
                tr_dot = self.board[y-1][x+1]
                mr_dot = self.board[y][x+1]
                if tc_dot.y_vector and tc_dot.x_vector and tr_dot.y_vector:
                    count += 1
                if dot.y_vector and bc_dot.x_vector and mr_dot.y_vector:
                    count += 1
                return count
        else:
            if dot.x == 0:
                bc_dot = self.board[y+1][x]
                mr_dot = self.board[y][x+1]
                return 1 if dot.x_vector and mr_dot.y_vector and bc_dot.x_vector else 0
            elif dot.x == len(self.board[0]) - 1:
                ml_dot = self.board[y][x-1]
                bl_dot = self.board[y+1][x-1]
                return 1 if ml_dot.y_vector and ml_dot.x_vector and bl_dot.x_vector else 0
            else:
                count = 0
                ml_dot = self.board[y][x-1]
                mr_dot = self.board[y][x+1]
                bl_dot = self.board[y+1][x-1]
                bc_dot = self.board[y+1][x]
                if ml_dot.x_vector and ml_dot.y_vector and bl_dot.x_vector:
                    count += 1
                if dot.x_vector and mr_dot.y_vector and bc_dot.x_vector:
                    count += 1
                return count
    
    def legal_move(self, x, y, vector):
        if vector == 'x':
            return self.board[y][x].can_set_x()
        else:
            return self.board[y][x].can_set_y()
    
    def update(self, x, y, vector):
        dot = self.board[y][x]
        if vector == 'x':
            dot.x_vector = True
        else:
            dot.y_vector = True
        return self.completed_boxes(dot, vector)


class Dot(object):
    def __init__(self, x, y, x_potential=True, y_potential=True, x_vector=False, y_vector=False):
        self.x =x
        self.y = y
        self.x_potential = x_potential
        self.y_potential = y_potential
        self.x_vector = x_vector
        self.y_vector = y_vector
    
    def can_set_x(self):
        if self.x_potential:
            if self.x_vector:
                raise ValueError(f"X vector already set for Dot at (x,y): {self.x},{self.y}.")
            else:
                return True
        else:
            raise ValueError(f"x_potential is False. X vector cannot be set for Dot at (x,y): {self.x},{self.y}.")

    def can_set_y(self):
        if self.y_potential:
            if self.y_vector:
                raise ValueError(f"Y vector already set for Dot at (x,y): {self.x},{self.y}.")
            else:
                return True
        else:
            raise ValueError(f"y_potential is False. Y vector cannot be set for Dot at (x,y): {self.x},{self.y}")

    def __str__(self):
        return f"Dot({self.x}, {self.y},  x_potential={self.x_potential}, y_potential={self.y_potential}, x_vector={self.x_vector}, y_vector={self.y_vector})"

    def __repr__(self):
        return f"Dot({self.x}, {self.y},  x_potential={self.x_potential}, y_potential={self.y_potential}, x_vector={self.x_vector}, y_vector={self.y_vector})"


if __name__ == '__main__':
    game = Game()
    game.start_sync()