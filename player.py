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
        found_holes = []
        for i in range(board.height):
            #Gutter/dip to the right
            found_holes = []
            for x in range(board.width - 1):
                if (x, i) in board.cells:
                    for y in range(i, board.height):
                        if (x+1, y) not in board.cells and (x+1, y) not in found_holes:
                            holes += i**exp_degree
                            found_holes.append((x+1, y))

            #Gutter/dip to the left
            for x in range(1, board.width):
                found_holes = []
                if (x, i) in board.cells:
                    for y in range(i, board.height):
                        if (x-1, y) not in board.cells and (x-1, y) not in found_holes:
                            holes += y**exp_degree
                            found_holes.append((x-1, y))

            #Sealed hole/overhang
            found_holes = []
            for x in range(board.width):
                if (x, i) in board.cells:
                    for y in range(i, board.height):
                        if (x, y) not in board.cells:
                            holes += y**(exp_degree+1)
        return holes



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
