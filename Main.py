from Game import *
from Mahjong import *
from Player import *
import logging

def main():
    east, south, west, north = HumanPlayer('East'), HumanPlayer('South'), HumanPlayer('West'), HumanPlayer('North')
    game = Game(players=[east, south, west, north])
    game.start()

if __name__ == "__main__":
    main()