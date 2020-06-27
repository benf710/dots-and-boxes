import asyncio
import random
import json

class Game(object):
    def __init__(self, player1=None, player2=None):
        self.player1 = player1
        self.player2 = player2
        self.is_player1_turn = None
        self.spectators = []
        self.board = Board()
        self.started = False

    def to_dict(self):
        p1 = self.player1
        p2 = self.player2
        if not self.started:
            return {'status': 'Waiting for another player to join.'}
        elif self.board.filled():
            winning_player = max(p1, p2, key=lambda player: player.score)
            game_status = f'Game over. Winner: {winning_player}'
        else:
            game_status = 'In progress'
        return {'status': game_status, 'board': self.board.out(), 'score': {p1.name: p1.score, p2.name: p2.score}, 'turn': p1.name if self.is_player1_turn else p2.name}

    def __str__(self):
        return json.dumps(self.to_dict())

    def start_async(self):
        self.started = True
        self.is_player1_turn = True
    
    def make_move(self, player, move_obj):
        if (player == self.player1) == self.is_player1_turn:
            if self.board.legal_move(move_obj['x'], move_obj['y'], move_obj['vector']):
                completed_boxes = self.board.update(move_obj['x'], move_obj['y'], move_obj['vector'])
                if completed_boxes == 0:
                    self.is_player1_turn = not self.is_player1_turn
                    status = {'status': 'success', 'message': f"You did not score any points."}
                    
                else:
                    if self.is_player1_turn:
                        self.player1.score += completed_boxes
                    else:
                        self.player2.score += completed_boxes
                    status = {'status': 'success', 'message': f"You scored {completed_boxes} points! Move again."}
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
    
    def out(self):
        printable = []
        for row in self.board:
            y_list = []
            for x in row:
                y_list.append(x.out())
            printable.append(y_list)
        return printable

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
    
    def out(self):
        return {'x': self.x, 'y': self.y, 'x_vector': self.x_vector, 'y_vector': self.y_vector}
    
    def can_set_x(self):
        return True if self.x_potential and not self.x_vector else False

    def can_set_y(self):
        return True if self.y_potential and not self.y_vector else False

    def __str__(self):
        return f"Dot({self.x}, {self.y},  x_potential={self.x_potential}, y_potential={self.y_potential}, x_vector={self.x_vector}, y_vector={self.y_vector})"

    def __repr__(self):
        return f"Dot({self.x}, {self.y},  x_potential={self.x_potential}, y_potential={self.y_potential}, x_vector={self.x_vector}, y_vector={self.y_vector})"
