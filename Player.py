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
        if not card is None: # dealer first draw card = None
            self.hidden.append(card)
        self.hidden = sorted(self.hidden)
    
    def anyActionSelf(self):
        """
        player has just draw a card
        hu or gang or discard a card
        """
        NotImplemented

    def anyActionOther(self, card, source_player):
        """
        card is played by other player
        peng, gang or hu or do nothing
        """
        NotImplemented

    def discard(self):
        """
        player discard a card, return the played card
        """
        NotImplemented

    def discardCard(self, card):
        """
        discard by card instance, return played card
        """
        return self.discardCardStr(str(card))

    def discardCardStr(self, card_str):
        """
        discard by card name
        """
        i = [str(x) for x in self.hidden].index(card_str)
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
        score = calcScore(self.revealed, self.hidden, 1)
        return score

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__()
        self.id = name
    
    def claimShortSuit(self):
        print(self.revealed + self.hidden)
        shortSuit = input(f"{self.id} Claim short suit [P/S/W]:")
        return shortSuit

    def anyActionSelf(self):
        print(self.revealed + self.hidden)
        action = input(f"{self.id} action: [GANG/HU/NOTHING]:")
        return action
    
    def discard(self):
        print(self.revealed + self.hidden)
        card_str = input(f"{self.id} play a card")
        return self.discardCardStr(card_str)

    def anyActionOther(self, card, source_player):
        print(self.revealed + self.hidden)
        action = input(f"{self.id} action on {source_player.id} playing {card}: [PENG/GANG/HU/NOTHING]:")
        return action

class DummyPlayer(Player):
    def __init__(self, id):
        super().__init__()
        self.id = f'Dummy_{id}'
    
    def claimShortSuit(self):
        return np.random.choice(['W','S','P'])
    
    def anyActionSelf(self):
        if self.hu() > 0:
            return "HU"
        else:
            return "NOTHING"
    
    def discard(self):
        discard_index = np.random.randint(0, len(self.hidden)-1)
        return self.hidden.pop(discard_index)

    def anyActionOther(self, card, source_player):
        if calcScore(self.revealed, self.hidden + [card], 0) > 0:
            return "HU"
        else:
            return "NOTHING"