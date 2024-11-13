from board import Direction, Rotation, Action, Shape
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError

#Default player
class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)
                
    def choose_action(self, board):
        #self.print_board(board)
        #time.sleep(0.5)

        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

#My player
class EpicPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)
                
    def choose_action(self, board):
        #self.print_board(board)
        #time.sleep(0.5)

        general_moveset = [Rotation.Anticlockwise, Rotation.Clockwise]
        #Stick to a side to avoid blocks averaging out to middle and filling fast, while leaving sides empty
        directional_move = [Direction.Left, Direction.Right, Direction.Down][self.random.randint(0, 2)];
        general_moveset.append(directional_move)

        tallest_col = 0
        if (len(board.cells) > 0):
            tallest_col = max(y for (x,y) in board.cells)

        if tallest_col > 20 and self.random.random() > 0.9:
            # 3% chance we'll discard or drop a bomb
            if board.discards_remaining > 0:
                return Action.Discard
            elif board.bombs_remaining > 0 and board.falling.shape != Shape.B:
                return Action.Bomb
            else:
                return self.random.choice(general_moveset)
        else:
            # 97% chance we'll make a normal move
            return self.random.choice(general_moveset)

SelectedPlayer = EpicPlayer
