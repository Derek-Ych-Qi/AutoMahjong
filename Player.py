import logging
from Mahjong import *

PLAYER_ACTIONS = ["NOTHING", "HU", "PENG", 'GANG']

class Player(object):
    def __init__(self):
        self.id = None
        self.game = None
        self.revealed = []
        self.hidden = []
        self.huList = []
        self.discardedList = []
        self.score = 0
        self.logger = logging.getLogger(self.id)
    
    def passThreeCards(self):
        NotImplemented

    def claimShortSuit(self):
        NotImplemented

    def draw(self, card):
        self.hidden.append(card)
        self.hidden = sorted(self.hidden)
    
    def anyAction(self):
        """
        player has just draw a card
        hu or gang or discard a card
        """
        NotImplemented

    def anyAction(self, card, source_player):
        """
        card is played by other player
        peng, gang or hu or do nothing
        """
        NotImplemented

    def discard(self, card):
        """
        player discard a card
        """
        i = [str(x) for x in self.hidden].index(str(card))
        return self.hidden.pop(i)
    
    def peng(self, card):
        i = [str(x) for x in self.hidden].index(str(card))
        j = [str(x) for x in self.hidden].index(str(card), i+1)
        if i == -1 or j == -1:
            return False
        card1 = self.hidden.pop(j)
        card2 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card])
        return True
    
    def gang(self, card):
        i = [str(x) for x in self.hidden].index(str(card))
        j = [str(x) for x in self.hidden].index(str(card), i+1)
        k = [str(x) for x in self.hidden].index(str(card), j+1)
        if i == -1 or j == -1 or k == -1:
            return False
        card1 = self.hidden.pop(j)
        card2 = self.hidden.pop(i)
        card3 = self.hidden.pop(k)
        self.revealed.append([card1, card2, card3, card])
        return True

    def hu(self):
        score, style = calcScore(self.revealed, self.hidden)
        return score

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__()
        self.id = name
    
    def claimShortSuit(self):
        print(self.revealed + self.hidden)
        shortSuit = input()
        return shortSuit

    def anyAction(self):
        print(self.revealed + self.hidden)
        action = input()
        return action
    
    def anyAction(self, card, source_player):
        print(card)
        print(self.revealed + self.hidden)
        action = input()
        return action
