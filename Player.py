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

    def draw(self, card:Mahjong):
        if card is None:
            # nothing
            pass
        else:
            if type(card) == list:
                self.hidden += card
            else:
                self.hidden.append(card)
        self.hidden = sorted(self.hidden)
    
    def checkHand(self) -> bool:
        return len(self.hidden) % 3 == 1

    def hashHand(self) -> tuple:
        revealed_tuple = tuple(tuple(k) for k in self.revealed)
        hidden_tuple = tuple(self.hidden)
        return revealed_tuple, hidden_tuple

    def anyActionSelf(self) -> str:
        """
        player has just draw a card
        hu or gang or discard a card
        """
        NotImplemented

    def anyActionOther(self, card:Mahjong, source_player) -> str:
        """
        card is played by other player
        peng, gang or hu or do nothing
        """
        NotImplemented

    def discard(self) -> Mahjong:
        """
        player discard a card, return the played card
        """
        NotImplemented

    def discardCard(self, card:Mahjong) -> Mahjong:
        """
        discard by card instance, return played card
        """
        return self.discardCardStr(str(card))

    def discardCardStr(self, card_str) -> Mahjong:
        """
        discard by card name
        """
        i = [str(x) for x in self.hidden].index(card_str)
        return self.hidden.pop(i)
    
    def canPeng(self, card) -> bool:
        hidden_str = [str(x) for x in self.hidden]
        return hidden_str.count(str(card)) >= 2

    def peng(self, card) -> bool:
        i = [str(x) for x in self.hidden].index(str(card))
        j = [str(x) for x in self.hidden].index(str(card), i+1)
        card1 = self.hidden.pop(j)
        card2 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card])
        return True
    
    def canGang(self, card, fromHand=False):
        hidden_str = [str(x) for x in self.hidden]
        if fromHand:
            #杠明刻
            for ket in self.revealed:
                if str(ket[0]) == str(card):
                    return True
            #暗杠
            if hidden_str.count(str(card)) >= 4:
                return True
            return False
        elif hidden_str.count(str(card)) >= 3: #明杠暗刻
            return True
        else:
            return False

    def gang(self, card, fromHand=False):
        if fromHand:
            for ket in self.revealed:
                if str(ket[0]) == str(card):
                    ket.append(card) #明杠
                    self.hidden.remove(card)
            return 1
        else:
            i = [str(x) for x in self.hidden].index(str(card))
            j = [str(x) for x in self.hidden].index(str(card), i+1)
            k = [str(x) for x in self.hidden].index(str(card), j+1)
            card1 = self.hidden.pop(k)
            card2 = self.hidden.pop(j)
            card3 = self.hidden.pop(i)
            self.revealed.append([card1, card2, card3, card])
            return 2 if fromHand else 1

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

    def getPublicInfo(self):
        info = {}
        info['shortSuit'] = self.shortSuit
        info['revealed'] = self.revealed
        info['played'] = self.discardedList
        info['hule'] = self.hule
        info['huList'] = self.huList
        return info


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
        if (self.hu() > 0) | any([self.canGang(card, fromHand=True) for card in self.hidden]):
            print(self.game.getPublicInfo())
            print(self.revealed + self.hidden)
            action = input(f"{self.id} action: [GANG/HU/NOTHING]:")
            return action
        else:
            return "NOTHING"
    
    def discard(self):
        #有缺打缺
        for i in range(len(self.hidden)):
            card = self.hidden[i]
            if card.suit == self.shortSuit:
                discard_index = i
                return self.hidden.pop(discard_index)
        print(self.game.getPublicInfo())
        print(self.revealed + self.hidden)
        card_str = input(f"{self.id} play a card:")
        return self.discardCardStr(card_str)

    def anyActionOther(self, card, source_player):
        self.ting()
        if card.suit == self.shortSuit:
            return "NOTHING"
        elif not (self.canGang(card) | self.canPeng(card) | (str(card) in [x[0] for x in self.tingList])):
            return "NOTHING"
        print(self.game.getPublicInfo())
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

def countKeAndPair(hidden):
    card_map = {}
    for card in hidden:
        card_map[str(card)] = card_map.get(str(card), 0) + 1
    return len([c for c, n in card_map.items() if n >= 2])

class SimpleAIPlayer(Player):
    def __init__(self, id):
        super().__init__()
        self.id = f"SimpleAI_{id}"
        self.planned = False
        self.oneSuit = None
        self.pengpeng = False
    
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
    
    def plan(self):
        """
        called after initial hand, make a brief game plan
        """
        _suit_lists = [0,0,0]
        for card in self.hidden:
            _suit_lists[ALL_SUITS.index(card.suit)] += 1
        if max(_suit_lists) >= 8:
            self.oneSuit = ALL_SUITS[_suit_lists.index(max(_suit_lists))] #清一色
        if countKeAndPair([c for c in self.hidden if c.suit != self.shortSuit]) >= 3:
            self.pengpeng = True
        self.planned = True
        

    def anyActionSelf(self):
        if self.hu() > 0:
            return "HU"
        else:
            return "NOTHING"
    
    def discard(self):
        if not self.planned:
            self.plan()
        #有缺打缺
        for i in range(len(self.hidden)):
            card = self.hidden[i]
            if card.suit == self.shortSuit:
                discard_index = i
                return self.hidden.pop(discard_index)
        
        if not self.oneSuit is None:
            #做清一色
            for i in range(len(self.hidden)):
                card = self.hidden[i]
                if card.suit != self.oneSuit:
                    discard_index = i
                    return self.hidden.pop(discard_index)

        #优先听牌
        discard_index = 999
        tingscore_list = []
        for i in range(len(self.hidden)):
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

        _suit_nums = {'W':[], 'S':[], 'P':[]}
        for card in self.hidden:
            _suit_nums[card.suit].append(card.num)
        _suit_nums_diff_map = {'W':[], 'S':[], 'P':[]}
        for suit in ALL_SUITS:
            if suit == self.shortSuit:
                continue
            _suit_nums_diff_map[suit] = list(np.abs(_suit_nums[suit] - np.mean(_suit_nums[suit])))
        _suit_nums_diff_list = _suit_nums_diff_map['P'] + _suit_nums_diff_map['S'] + _suit_nums_diff_map['W'] #  sequence of this should be corresponding to self.hidden

        cardCount = [self.hidden.count(card) for card in self.hidden]
        discardRange = [i for i in range(len(self.hidden)) if cardCount[i] < 2]
        diff_discard = [_suit_nums_diff_list[i] for i in discardRange]
        if len(discardRange) == 0:
            return self.hidden.pop(np.random.choice(range(len(self.hidden))))
        maxdiff = max(diff_discard)
        discard_index = discardRange[diff_discard.index(maxdiff)]

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
    
