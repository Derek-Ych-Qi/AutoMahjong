import logging
from Mahjong import *

PLAYER_ACTIONS = ["NOTHING", "HU", "PENG", 'GANG']

class Player(object):
    def __init__(self):
        self.id = None
        self.game = None
        self.revealed = []
        self.hidden = []
        self.hule = False
        self.huList = []
        self.tingList = []
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
        card1 = self.hidden.pop(j)
        card2 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card])
        return True
    
    def gang(self, card):
        i = [str(x) for x in self.hidden].index(str(card))
        j = [str(x) for x in self.hidden].index(str(card), i+1)
        k = [str(x) for x in self.hidden].index(str(card), j+1)
        card1 = self.hidden.pop(k)
        card2 = self.hidden.pop(j)
        card3 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card3, card])
        return True

    def hu(self):
        score = calcScore(self.revealed, self.hidden, 1)
        return score
    
    def ting(self):
        self.tingList = tingpai(self.revealed, self.hidden)

    def endGameSummary(self):
        print('=' * 100)
        print(f"{self.id} score={self.score}")
        print(f"Hand {self.revealed + self.hidden}")
        if self.hule:
            print(self.huList)
        self.ting()
        print(self.tingList)

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__()
        self.id = name
    
    def passThreeCards(self):
        _suit_map = {'W':0, 'P':0, 'S':0}
        for card in self.hidden:
            _suit_map[card.suit] += 1
        print(self.hidden)
        while True:
            passingCards = []
            passing_suit = input(f"{self.id} Passing suit [P/S/W]:")
            if _suit_map[passing_suit] < 3:
                print(f"Invalid passing suit {passing_suit}")
                continue
            passing_num = input(f"{self.id} passing nums [X,Y,Z]:").split(',')
            for s in passing_num:
                cardStr = f'{s}{passing_suit}'
                passingCards.append(self.discardCardStr(cardStr))
            if len(passingCards) == 3:
                break
        return passingCards

    def claimShortSuit(self):
        print(self.hidden)
        shortSuit = input(f"{self.id} Claim short suit [P/S/W]:")
        self.shortSuit = shortSuit
        print(f"{self.id} short suit is {shortSuit}")
        return shortSuit

    def anyActionSelf(self):
        print(self.revealed + self.hidden)
        action = input(f"{self.id} action: [GANG/HU/NOTHING]:")
        return action
    
    def discard(self):
        print(self.revealed + self.hidden)
        card_str = input(f"{self.id} play a card:")
        return self.discardCardStr(card_str)

    def anyActionOther(self, card, source_player):
        print(self.revealed + self.hidden)
        action = input(f"{self.id} action on {source_player.id} playing {card}: [PENG/GANG/HU/NOTHING]:")
        return action

class DummyPlayer(Player):
    def __init__(self, id):
        super().__init__()
        self.id = f'Dummy_{id}'
    
    def passThreeCards(self):
        _suit_map = {'W':0, 'P':0, 'S':0}
        for card in self.hidden:
            _suit_map[card.suit] += 1
        _suits = ['W', 'S', 'P']
        np.random.shuffle(_suits)
        for suit in _suits:
            if _suit_map[suit] >= 3:
                passingSuit = suit
                break
        _passing = np.random.choice([x for x in self.hidden if x.suit == passingSuit], 3, replace=False)
        return [self.discardCard(x) for x in _passing]

    def claimShortSuit(self):
        _suit_map = {'W':0, 'P':0, 'S':0}
        for card in self.hidden:
            _suit_map[card.suit] += 1
        shortSuit = 'W'
        for suit in ['S', 'P']:
            if _suit_map[suit] < _suit_map[shortSuit]:
                shortSuit = suit
        self.shortSuit = shortSuit
        print(f"{self.id} short suit is {shortSuit}")
        return shortSuit
    
    def anyActionSelf(self):
        if self.hu() > 0:
            return "HU"
        else:
            return "NOTHING"
    
    def discard(self):
        discard_index = np.random.randint(0, len(self.hidden)-1)
        for i in range(len(self.hidden)):
            card = self.hidden[i]
            if card.suit == self.shortSuit:
                discard_index = i
                break
        return self.hidden.pop(discard_index)

    def anyActionOther(self, card, source_player):
        if calcScore(self.revealed, self.hidden + [card], 0) > 0:
            return "HU"
        else:
            return "NOTHING"