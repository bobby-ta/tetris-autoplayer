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
        self.move_sequences = {}
        for shape in [Shape.L, Shape.J, Shape.T, Shape.S, Shape.Z, Shape.O, Shape.I]:
            self.move_sequences[shape] = [[], []]
            self.move_sequences[shape][0], self.move_sequences[shape][1] = self.gen_move_sequences(shape)

    #Return unique rotations for each shape
    def spin_combos(self, shape):
        if shape == Shape.Z or shape == Shape.S:
            #S and Z bias left/rightwards depending on stage of spin - look into it later
            return [None, Rotation.Clockwise, [Rotation.Clockwise, Rotation.Clockwise]]
        elif shape == Shape.L or shape == Shape.J or shape == Shape.T:
            return [None, Rotation.Clockwise, [Rotation.Clockwise, Rotation.Clockwise], [Rotation.Anticlockwise]]
        else: #bomb or O or I (why would u ever make I horizontal)
            return [None]
    
    #Return all possible move sequences
    def gen_move_sequences(self, shape):
        spin_combos = self.spin_combos(shape)

        sequences_left = []
        sequences_right = []
        for spin_combo in spin_combos: #e.g. [Rotation.Clockwise, Rotation.Clockwise]
            if spin_combo is None:
                spin_combo = []

            #Shift left
            for i in range(7):
                if isinstance(spin_combo, list):
                    sequences_left.append(spin_combo + ([Direction.Left] * i) + [Direction.Drop])
                else:
                    sequences_left.append([spin_combo] + ([Direction.Left] * i) + [Direction.Drop])

            #Shift right
            for i in range(1, 5): #maximum of 4 rights need to be taken
                if isinstance(spin_combo, list):
                    sequences_right.append(spin_combo + ([Direction.Right] * i) + [Direction.Drop])
                else:
                    sequences_right.append([spin_combo] + ([Direction.Right] * i) + [Direction.Drop])
            

        return sequences_left, sequences_right

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
            bumpiness += abs(min((y for (x, y) in board.cells if x == i), default=24) - min((y for (x, y) in board.cells if x == i+1), default=24))
        return bumpiness
    
    #Maximise
    def lines_cleared(self, current_score, temp_clone):
        #Compare score before and after placing block
        #Lines are cleared on drop, so score will update
        lines_cleared = ((temp_clone.score - current_score) // 25)
        if lines_cleared <= 2:
            return 1 #score 25
        elif lines_cleared > 2:
            return 2 #score 100
        elif lines_cleared > 4:
            return 3 #score 400
        elif lines_cleared > 16:
            return 1000000 #score 1600
    
    def cont_vertical(self, board):
        continuous_holes = 0
        for i in range(board.width):
            for j in range(min((y for (x, y) in board.cells if x == i), default = 23), board.height - 1):
                if (i, j) not in board.cells and (i, j+1) not in board.cells:
                    continuous_holes += 1
        return continuous_holes
    
    def cont_horizontal(self, board):
        continuous_holes = 0
        for i in range(board.width - 1):
            for j in range(min((y for (x, y) in board.cells if x == i), default = 23), board.height):
                if (i, j) not in board.cells and (i+1, j) not in board.cells:
                    continuous_holes += 1
        return continuous_holes

    #Returns coordinate of highest
    def highest_in_col(self, board, col):
        return min((y for (x, y) in board.cells if x == col), default=24)
    
    #Returns height of highest
    def max_height_in_col(self, board, col):
        return 24 - min((y for (x, y) in board.cells if x == col), default=24)
    
    def holes(self, board):
        holes = 0
        for i in range(board.width):
            highest_in_col = self.highest_in_col(board, i)
            if highest_in_col < 23:
                for j in range(highest_in_col+1, board.height): 
                    if (i, j) not in board.cells:
                        holes += 1
        return holes
    
    def max_height(self, board):
        return 24 - min((y for (x, y) in board.cells), default=24)
    
    def calc_gutters(self, board):
        gutters = 0
        #Col 0 lower than col 1
        if self.max_height_in_col(board, 0) - self.max_height_in_col(board, 1) <= -4:
            gutters += 1
        for i in range(1, board.width - 1):
            #Lower than both neighbours
            if (self.max_height_in_col(board, i) - self.max_height_in_col(board, i+1) <= -4) and (self.max_height_in_col(board, i) - self.max_height_in_col(board, i-1) <= -4):
                gutters += 1
        #Col 9 lower than col 8
        if self.max_height_in_col(board, 9) - self.max_height_in_col(board, 8) <= -4:
            gutters += 1

        if self.max_height(board) > 9:
            return -gutters
        if gutters == 1:
            return 0.3
        else:
            return -gutters
    
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
        #SET UP CURRENT MOVE
        current_score = board.score
        temp_clone = board.clone()
        self.simulate_move_sequence(temp_clone, move_sequence)
        
        #TRY EACH POSSIBLE NEXT MOVE
        #Find best-case scenario for after next move
        max_score = -1000000000 #this will be the max score FOR THE CURRENTLY EVALUATED MOVE
        for move_sequence2 in self.move_sequences[board.falling.shape]:
            #try:
                next_step_clone = temp_clone.clone()
                self.simulate_move_sequence(next_step_clone, move_sequence2)

                #Heuristics
                aggregate_height = self.aggregate_height(next_step_clone)
                avg_height = aggregate_height / board.width
                max_height = self.max_height(next_step_clone)
                lines_cleared = self.lines_cleared(current_score, next_step_clone)
                bumpiness = self.bumpiness(next_step_clone)
                holes = self.holes(next_step_clone)
                cont_horizontal = self.cont_horizontal(next_step_clone)
                cont_vertical = self.cont_vertical(next_step_clone)
                calc_gutters = self.calc_gutters(next_step_clone)
                
                #Weights
                aggregate_height_weight = -0
                avg_height_weight = -0.10
                max_height_weight = -0.025
                lines_cleared_weight = 0
                bumpiness_weight = -0.39
                holes_weight = -2.5
                cont_horizontal_weight = -0.2
                cont_vertical_weight = -0.3
                calc_gutters_weight = 5

                score = aggregate_height * aggregate_height_weight + avg_height * avg_height_weight + max_height * max_height_weight + lines_cleared * lines_cleared_weight + bumpiness * bumpiness_weight + holes * holes_weight + cont_horizontal * cont_horizontal_weight + cont_vertical * cont_vertical_weight + calc_gutters * calc_gutters_weight

                #print(aggregate_height * aggregate_height_weight, avg_height * avg_height_weight, max_height * max_height_weight, lines_cleared * lines_cleared_weight, bumpiness * bumpiness_weight, holes * holes_weight, cont_horizontal * cont_horizontal_weight, cont_vertical * cont_vertical_weight, score)

                if score > max_score:
                    max_score = score

            #except:
                #pass

        return max_score

    def choose_action(self, board):
        #try:
            max_coefficient = -1000000000 #This will be the max score for ALL THE MOVES
            best_sequence = None

            #Check moves shifting to left
            for move_sequence in self.move_sequences[board.falling.shape][0]:
                current_coefficient = self.evaluate_move_sequence(board, move_sequence)
                if current_coefficient > max_coefficient:
                    max_coefficient = current_coefficient
                    best_sequence = move_sequence
                if board.falling.shape is not None and board.falling.left == 0:
                    break #Avoid redundant movesets
            
            #Check moves shifting to right
            for move_sequence in self.move_sequences[board.falling.shape][1]:
                current_coefficient = self.evaluate_move_sequence(board, move_sequence)
                if current_coefficient > max_coefficient:
                    max_coefficient = current_coefficient
                    best_sequence = move_sequence
    
                if board.falling.shape is not None and board.falling.right == 9:
                    break #Avoid redundant movesets
        
            return best_sequence
        #except:
            #return Direction.Down
        

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
