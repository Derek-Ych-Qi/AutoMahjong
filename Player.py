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
        if card is None:
            # nothing
            pass
        else:
            if type(card) == list:
                self.hidden += card
            else:
                self.hidden.append(card)
        self.hidden = sorted(self.hidden)
    
    def checkHand(self):
        return len(self.hidden) % 3 == 1

    def hashHand(self):
        revealed_tuple = tuple(tuple(k) for k in self.revealed)
        hidden_tuple = tuple(self.hidden)
        return revealed_tuple, hidden_tuple

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
    
    def canPeng(self, card):
        hidden_str = [str(x) for x in self.hidden]
        return hidden_str.count(str(card)) >= 2

    def peng(self, card):
        i = [str(x) for x in self.hidden].index(str(card))
        j = [str(x) for x in self.hidden].index(str(card), i+1)
        card1 = self.hidden.pop(j)
        card2 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card])
        return True
    
    def canGang(self, card):
        hidden_str = [str(x) for x in self.hidden]
        if hidden_str.count(str(card)) >= 3:
            return True
        else:
            for ket in self.revealed:
                if str(ket[0]) == str(card):
                    return True
            return False

    def gang(self, card):
        for ket in self.revealed:
            if str(ket[0]) == str(card):
                ket.append(card) #明杠
                return True

        i = [str(x) for x in self.hidden].index(str(card))
        j = [str(x) for x in self.hidden].index(str(card), i+1)
        k = [str(x) for x in self.hidden].index(str(card), j+1)
        card1 = self.hidden.pop(k)
        card2 = self.hidden.pop(j)
        card3 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card3, card]) #暗杠
        return True

    def hu(self):
        score = calcScore( *self.hashHand(), zimo_fan=1)
        return score
    
    def ting(self):
        self.tingList = tingpai(*self.hashHand())

    def currentState(self):
        print('=' * 100)
        print(f"{self.id} score={self.score}")
        print(f"Hand {self.revealed + self.hidden}")
        if self.hule:
            print(f"Hu list {self.huList}")
        self.ting()
        print(f"Ting list {self.tingList}")

### Implementation

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
        revealed_tuple, hidden_tuple = self.hashHand()
        if calcScore( revealed_tuple, tuple(self.hidden + [card]), 0) > 0:
            return "HU"
        else:
            return "NOTHING"

class SimpleAIPlayer(Player):
    def __init__(self, id):
        super().__init__()
        self.id = f"SimpleAI_{id}"
    
    def passThreeCards(self):
        _suit_map = {'W':[], 'P':[], 'S':[]}
        for card in self.hidden:
            _suit_map[card.suit].append(card)
        suits = ['W', 'P', 'S']
        np.random.shuffle(suits)
        min_cards = 9
        for suit in suits:
            if len(_suit_map[suit]) < 3:
                continue
            elif len(_suit_map[suit]) <= min_cards:
                passingSuit = suit
                min_cards = len(_suit_map[suit])
        _passing = np.random.choice(_suit_map[passingSuit], 3, replace=False)
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
        tingscore_list = []
        for i in range(len(self.hidden)):
            card = self.hidden[i]
            if card.suit == self.shortSuit:
                discard_index = i
                break
            if i == 0:
                fake_hidden = self.hidden[1:]
            elif i == len(self.hidden)-1:
                fake_hidden = self.hidden[0:i-1]
            else:
                fake_hidden = self.hidden[0:i-1] + self.hidden[i+1:]
            revealed_tuple, hidden_tuple = self.hashHand()
            tinglist = tingpai( revealed_tuple, tuple(fake_hidden))
            tingscore = 0
            for ting in tinglist:
                tingscore += ting[1] # FIXME multiply by remaining cards
            tingscore_list.append(tingscore)
        
        if len(tingscore_list) > 0 and max(tingscore_list) > 0:
            discard_index = tingscore_list.index(max(tingscore_list))
        else:
            pass

        return self.hidden.pop(discard_index)

    def anyActionOther(self, card, source_player):
        revealed_tuple, hidden_tuple = self.hashHand()
        if calcScore( revealed_tuple, tuple(self.hidden + [card]), 0) > 0:
            return "HU"
        elif self.canGang(card):
            return "GANG"
        elif self.canPeng(card):
            return "PENG"
        else:
            return "NOTHING"
    
