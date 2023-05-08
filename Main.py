from Game import *
from Mahjong import *
from PlayerImpl import *
import logging
logging.basicConfig(level="INFO")

import numpy as np
#np.random.seed(53)

def main():
    #east, south, west, north = HumanPlayer('East'), HumanPlayer('South'), HumanPlayer('West'), HumanPlayer('North')
    east, south, west, north = SimpleAIPlayer(101), SimpleAIPlayer(102), SimpleAIPlayer(103), CheatingPlayer(900)
    #east, south, west, north = HumanPlayer('Catherine'), CheatingPlayer(901), CheatingPlayer(902), CheatingPlayer(903)
    #east, south, west, north = DummyPlayer(0), DummyPlayer(1), DummyPlayer(2), DummyPlayer(3)
    game = Game(players=[east, south, west, north], verbose=True, observer=Observer(), seed=1881683970)
    game.start()

if __name__ == "__main__":
    main()