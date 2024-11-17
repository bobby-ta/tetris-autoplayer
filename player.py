from board import Direction, Rotation, Action, Shape, NoBlockException
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
            aggregate_height += 23 - min((y for (x, y) in board.cells if x == i), default=23)
        return aggregate_height
    
    #Minimise
    def bumpiness(self, board):
        bumpiness = 0
        for i in range(board.width - 1):
            bumpiness += abs(min((y for (x, y) in board.cells if x == i), default=23) - min((y for (x, y) in board.cells if x == i+1), default=23))
        return bumpiness
    
    #Maximise
    def lines_cleared(self, current_score, temp_clone):
        #Compare score before and after placing block
        #Lines are cleared on drop, so score will update
        return ((temp_clone.score - current_score) // 25)**3 * 25
        
    
    
    #Minimise
    def holes(self, board):
        holes = 0
        exp_degree = 4
        holes_already_found = set()
        for y in range(board.height):
            for x in range(board.width):
                if (x, y) in board.cells: #Do for every block cell
                    for i in range(y, board.height): #Explore all cells below block
                            #Sealed hole/overhang
                            #Punish VERY heavily
                            #Maybe even heavier
                            if (x, i) not in board.cells and (x, i) not in holes_already_found:
                                holes += (24-i)**(exp_degree)+20
                                holes_already_found.add((x, i))
        return holes

    def gutters(self, board):
        gutters = 0
        exp_degree = 2
        gutters_right = set()
        gutters_left = set()
        for y in range(board.height):
            for x in range(board.width):
                if (x, y) in board.cells: #Do for every block cell
                    for i in range(y, board.height): #Explore all cells below block
                            #Right
                            if x < board.width - 1: #Can't be rightmost column
                                if (x+1, i) not in board.cells and (x+1, i) not in gutters_right:
                                    gutters += (24-i)**exp_degree
                                    gutters_right.add((x+1, i))
                            
                            #Left
                            if x > 0: #Can't be leftmost column
                                if (x-1, i) not in board.cells and (x-1, i) not in gutters_left:
                                    gutters += (24-i)**exp_degree
                                    gutters_left.add((x-1, i))
        return gutters
    
    def max_height(self, board):
        return 23 - min((y for (x, y) in board.cells), default=23)

    #Return unique rotations for each shape
    def spin_combos(self, board):
        if board.falling.shape == Shape.Z or board.falling.shape == Shape.S:
            #S and Z bias left/rightwards depending on stage of spin - look into it later
            return [None, Rotation.Clockwise, [Rotation.Clockwise, Rotation.Clockwise]]
        elif board.falling.shape == Shape.L or board.falling.shape == Shape.J or board.falling.shape == Shape.T:
            return [None, Rotation.Clockwise, [Rotation.Clockwise, Rotation.Clockwise], [Rotation.Anticlockwise]]
        else: #bomb or O or I (why would u ever make I horizontal)
            return [None]
    
    #Return all possible move sequences
    def move_sequences(self, board):
        spin_combos = self.spin_combos(board)
        move_sequences = []
        for i in spin_combos: #e.g. [Rotation.Clockwise, Rotation.Clockwise]
            temp_clone = board.clone()
            if i is None:
                spin_combo = []
            else:
                spin_combo = i
            
            #Spin before shifting to avoid redundant/missing shifts
            if isinstance(spin_combo, list):
                #Iterate through individual rotations in complex spin
                for individual_rotation in spin_combo: #e.g. Rotation.Clockwise
                    temp_clone.falling.rotate(individual_rotation, temp_clone)
            else:
                temp_clone.falling.rotate(spin_combo, temp_clone)

            #Shift left
            dist_left = temp_clone.falling.left
            for i in range(dist_left + 1):
                if isinstance(spin_combo, list):
                    move_sequences.append(spin_combo + ([Direction.Left] * i) + [Direction.Drop])
                else:
                    move_sequences.append([spin_combo] + ([Direction.Left] * i) + [Direction.Drop])

            #Shift right
            dist_right = temp_clone.width - temp_clone.falling.right
            if temp_clone.falling.shape != Shape.I and min((y for (x, y) in temp_clone.cells), default=23) > 16:
                dist_right -= 1
            for i in range(1, dist_right):
                if isinstance(spin_combo, list):
                    move_sequences.append(spin_combo + ([Direction.Right] * i) + [Direction.Drop])
                else:
                    move_sequences.append([spin_combo] + ([Direction.Right] * i) + [Direction.Drop])
            

        return move_sequences
    
    #Run move sequence on clone
    def simulate_move_sequence(self, board, move_sequence):
        try:
            for move in move_sequence:
                if isinstance(move, Rotation):
                    board.rotate(move)
                elif isinstance(move, Direction):
                    board.move(move)
        except NoBlockException:
            pass

    #Evaluate move sequence
    def evaluate_move_sequence(self, board, move_sequence):
        current_score = board.score
        temp_clone = board.clone()
        self.simulate_move_sequence(temp_clone, move_sequence)
        
        
        aggregate_height = self.aggregate_height(temp_clone)
        bumpiness = self.bumpiness(temp_clone)
        lines_cleared = self.lines_cleared(current_score, temp_clone)
        holes = self.holes(temp_clone)
        gutters = self.gutters(temp_clone)
        max_height = self.max_height(temp_clone)

        lines_cleared_weight = 1
        #Make dependent on height - stacks to top in endgame
        try:
            holes_weight = -6 / aggregate_height
        except ZeroDivisionError: #Flat board
            holes_weight = -0.75

        gutters_weight = holes_weight
        aggregate_height_weight = -0.1 #conservative
        bumpiness_weight = -0.150

        if (lines_cleared > 0):
            print((lines_cleared * lines_cleared_weight), (holes * holes_weight), (aggregate_height * aggregate_height_weight), (bumpiness * bumpiness_weight), (gutters * gutters_weight))

        return (lines_cleared * lines_cleared_weight) + (holes * holes_weight) + (aggregate_height * aggregate_height_weight) + (bumpiness * bumpiness_weight) + (gutters * gutters_weight)

    def choose_action(self, board):
        max_coefficient = -1000000000
        best_sequence = None
        for move_sequence in self.move_sequences(board):
            if self.evaluate_move_sequence(board, move_sequence) > max_coefficient:
                max_coefficient = self.evaluate_move_sequence(board, move_sequence)
                best_sequence = move_sequence
        
        return best_sequence
        

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
