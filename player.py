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
        lines_cleared = ((temp_clone.score - current_score) // 25)
        if lines_cleared == 1:
            return 4
        elif lines_cleared == 2:
            return 16
        elif lines_cleared == 3:
            return 64
        elif lines_cleared == 4:
            return 256
    
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

    def holes(self, board):
        holes = 0
        exp_degree = 4
        holes_already_found = set()
        for i in range(board.width):
            for j in range(min((y for (x, y) in board.cells if x == i), default = 23), board.height): #Explore all cells below block
                    #Sealed hole/overhang
                    #Punish VERY heavily
                    #Maybe even heavier
                    if (i, j) not in board.cells and (i, j) not in holes_already_found:
                        holes += 1
                        holes_already_found.add((i, j))
        return holes
    
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
        #TRY CURRENT MOVE
        current_score = board.score
        temp_clone = board.clone()
        self.simulate_move_sequence(temp_clone, move_sequence)
        
        #TRY NEXT MOVE
        #Find best-case scenario for after next move
        max_score = -1000000000 #this will be the max score FOR THE CURRENTLY EVALUATED MOVE
        for move_sequence in self.move_sequences(temp_clone):
            try:
                next_step_clone = temp_clone.clone()
                self.simulate_move_sequence(next_step_clone, move_sequence)

                #Heuristics
                aggregate_height = self.aggregate_height(next_step_clone)
                avg_height = aggregate_height / board.width
                max_height = self.max_height(next_step_clone)
                lines_cleared = self.lines_cleared(current_score, next_step_clone)
                bumpiness = self.bumpiness(next_step_clone)
                holes = self.holes(next_step_clone)
                cont_horizontal = self.cont_horizontal(next_step_clone)
                cont_vertical = self.cont_vertical(next_step_clone)
                
                #Weights
                aggregate_height_weight = -0
                avg_height_weight = -0.2
                max_height_weight = -0.3
                lines_cleared_weight = 1.075
                bumpiness_weight = -0.4
                holes_weight = -2.55
                cont_horizontal_weight = -0.2
                cont_vertical_weight = -0.4

                score = aggregate_height * aggregate_height_weight + avg_height * avg_height_weight + max_height * max_height_weight + lines_cleared * lines_cleared_weight + bumpiness * bumpiness_weight + holes * holes_weight + cont_horizontal * cont_horizontal_weight + cont_vertical * cont_vertical_weight

                print(aggregate_height * aggregate_height_weight, avg_height * avg_height_weight, max_height * max_height_weight, lines_cleared * lines_cleared_weight, bumpiness * bumpiness_weight, holes * holes_weight, cont_horizontal * cont_horizontal_weight, cont_vertical * cont_vertical_weight, score)

                if score > max_score:
                    max_score = score

            except:
                pass

        return max_score

    def choose_action(self, board):
        try:
            max_coefficient = -1000000000 #This will be the max score for ALL THE MOVES
            best_sequence = None
            for move_sequence in self.move_sequences(board):
                if self.evaluate_move_sequence(board, move_sequence) > max_coefficient:
                    max_coefficient = self.evaluate_move_sequence(board, move_sequence)
                    best_sequence = move_sequence
            
            return best_sequence
        except:
            return Direction.Down
        

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
