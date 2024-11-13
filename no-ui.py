from adversary import RandomAdversary
from arguments import parser
from board import Board, Direction, Rotation, Action, Shape
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, \
    BLOCK_LIMIT
from exceptions import BlockLimitException
from player import Player, SelectedPlayer

def run():
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(DEFAULT_SEED, BLOCK_LIMIT)
    player = SelectedPlayer()

    try:
        for move in board.run(player, adversary):
            pass
    except BlockLimitException:
        pass
    print(max(y for (x,y) in board.cells))
    print(board.height)
    return board.score

print(run())