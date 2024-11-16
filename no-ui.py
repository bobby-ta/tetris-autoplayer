from adversary import RandomAdversary
from arguments import parser
from board import Board, Direction, Rotation, Action, Shape
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, \
    BLOCK_LIMIT
from exceptions import BlockLimitException
from player import Player, SelectedPlayer
import random

def run():
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    seed = random.randint(0, 1000000)
    adversary = RandomAdversary(seed, BLOCK_LIMIT)
    player = SelectedPlayer()

    try:
        for move in board.run(player, adversary):
            pass
    except BlockLimitException:
        print("Ran out of blocks")
    if board.score < 12000:
        print("Bad seed:", seed)
    return board.score

scores = []
for i in range(20):
    scores.append(run())
scores.sort()
print("Median:", scores[9])