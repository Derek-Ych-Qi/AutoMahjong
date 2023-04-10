from Game import *
from Mahjong import *
from Player import *
import logging
logging.basicConfig(level="INFO")

import numpy as np
np.random.seed(42)

def main():
    #east, south, west, north = HumanPlayer('East'), HumanPlayer('South'), HumanPlayer('West'), HumanPlayer('North')
    east, south, west, north = SimpleAIPlayer(100), SimpleAIPlayer(101), SimpleAIPlayer(102), SimpleAIPlayer(103)
    #east, south, west, north = DummyPlayer(0), DummyPlayer(1), DummyPlayer(2), DummyPlayer(3)
    game = Game(players=[east, south, west, north])
    game.start()

if __name__ == "__main__":
    main()