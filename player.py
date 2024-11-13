from board import Direction, Rotation, Action, Shape
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError

#My player
class EpicPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    #Minimise
    def aggregate_height(self, board):
        aggregate_height = 0
        for i in range(board.width):
            aggregate_height += 23 - min((y for (x, y) in board.cells if x == i), default=0)
        return aggregate_height
    
    #Minimise
    def bumpiness(self, board):
        bumpiness = 0
        for i in range(board.width - 1):
            bumpiness += abs(min((y for (x, y) in board.cells if x == i), default=0) - min((y for (x, y) in board.cells if x == i+1), default=0))
        return bumpiness
    
    #Maximise
    def complete_lines(self, board):
        complete_lines = 0
        for y in range(board.height):
            if all((x, y) in board.cells for x in range(board.width)):
                complete_lines += 1
        return complete_lines
    
    #Minimise
    def holes(self, board):
        holes = 0
        exp_degree = 2
        holes_right = set()
        holes_left = set()
        holes_under = set()
        for y in range(board.height):
            for x in range(board.width):
                if (x, y) in board.cells: #Do for every block cell
                    for i in range(y, board.height): #Explore all cells below block
                            
                            #GUTTER/DIP TO THE RIGHT
                            if x < board.width - 1: #Can't be rightmost column
                                if (x+1, i) not in board.cells and (x+1, i) not in holes_right:
                                    holes += i**exp_degree
                                    holes_right.add((x+1, i))
                            
                            #GUTTER/DIP TO THE LEFT
                            if x > 0: #Can't be leftmost column
                                if (x-1, i) not in board.cells and (x-1, i) not in holes_left:
                                    holes += i**exp_degree
                                    holes_left.add((x-1, i))

                            #Sealed hole/overhang
                            if (x, i) not in board.cells and (x, i) not in holes_under:
                                holes += i**(exp_degree + 1)
                                holes_under.add((x, i))
        return holes

    def simulate_current_move(self, board, action):
        new_board = board.copy()
        

    def choose_action(self, board):
        

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

SelectedPlayer = EpicPlayer
