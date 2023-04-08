from Game import *
from Mahjong import *
from Player import *
import logging
logging.basicConfig(level="INFO")

def main():
    #east, south, west, north = HumanPlayer('East'), HumanPlayer('South'), HumanPlayer('West'), HumanPlayer('North')
    #east, south, west, north = HumanPlayer('MyName'), DummyPlayer(1), DummyPlayer(2), DummyPlayer(3)
    east, south, west, north = DummyPlayer(0), DummyPlayer(1), DummyPlayer(2), DummyPlayer(3)
    game = Game(players=[east, south, west, north])
    game.start()

if __name__ == "__main__":
    main()