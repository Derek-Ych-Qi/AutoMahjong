import logging
import datetime
import numpy as np

from Mahjong import *
from Player import *

class Game(object):
    def __init__(self):
        self.players = []
        self.deck = []

    def nextRound(self):
        curr_player = getNext(self.prev_player).draw()
        discarded = curr_player.discard()
        for player in self.players:
            if player.anyaction(discarded):
                self.prev_player = player
        self.prev_player = curr_player
    
    def start(self):
        while self.deck:
            self.nextRound()
        self.score()
        self.end()

    def score(self):
    
    def end(self):