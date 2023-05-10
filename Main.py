from Game import *
from Mahjong import *
from PlayerImpl import *
import logging
from collections import deque
logging.basicConfig(level="INFO")

import numpy as np
#np.random.seed(53)

def main():
    east, south, west, north = CheatingPlayer(900), SimpleAIPlayer(101), RandomAIPlayer(102, 0.01), RandomAIPlayer(103, 0.1)
    players = deque([east, south, west, north])
    players.rotate(2)
    game = Game(players=list(players), verbose=True, observer=Observer(), seed=330474236)
    game.start()

if __name__ == "__main__":
    main()