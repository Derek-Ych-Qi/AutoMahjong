from Player import *
import pdb

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
        return shortSuit

    def anyActionSelf(self):
        if (self.hu() > 0) | any([self.canGang(card, fromHand=True) for card in self.hidden]):
            self.game.displayPublicInfo()
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
        self.game.displayPublicInfo()
        print(self.revealed + self.hidden)
        card_str = input(f"{self.id} play a card:")
        return self.discardCardStr(card_str)

    def anyActionOther(self, card, source_player):
        self.ting()
        if card.suit == self.shortSuit:
            return "NOTHING"
        elif not (self.canGang(card) | self.canPeng(card) | (str(card) in [x[0] for x in self.tingList])):
            return "NOTHING"
        self.game.displayPublicInfo()
        print(self.revealed + self.hidden)
        action = input(f"{self.id} action on {source_player.id} playing {card}: [PENG/GANG/HU/NOTHING]:")
        return action

############################################################################################################

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

############################################################################################################

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
        min_cards = 14
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

    def inRevealed(self, cardstr):
        return sum([sum([cardsToStr(x).count(cardstr) for x in p.revealed]) for p in self.game.players])

    def played(self, cardstr):
        return sum([cardsToStr(p.discardedList).count(cardstr) for p in self.game.players])

    def playedAndInRevealed(self, cardstr):
        played, in_revealed = self.played(cardstr), self.inRevealed(cardstr)
        return played + in_revealed

    def anyActionSelf(self):
        if self.hu() > 0:
            return "HU"
        elif any( [self.canGang(card) for card in self.hidden] ):
            return "GANG"
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
                fake_hidden = self.hidden[0:i]
            else:
                fake_hidden = self.hidden[0:i] + self.hidden[i+1:]
            revealed_tuple, hidden_tuple = self.hashHand()
            tinglist = tingpai( revealed_tuple, tuple(fake_hidden))
            tingscore = 0
            for ting in tinglist:
                numRemaining = 4-self.playedAndInRevealed(str(ting[0]))
                tingscore += ting[1] * numRemaining if numRemaining > 0 else 0.01 #听死牌好于不听牌
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
            if suit == self.shortSuit or len(_suit_nums[suit]) == 0:
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
        if self.oneSuit and card.suit != self.oneSuit:
            return "NOTHING"

        revealed_tuple, hidden_tuple = self.hashHand()
        if calcScore( revealed_tuple, tuple(self.hidden + [card]), 0) > 0:
            return "HU"
        elif self.canGang(card):
            return "GANG"
        elif self.canPeng(card):
            if card in self.discardedList:
                return "NOTHING"
            elif self.oneSuit is None:
                return "PENG"
            elif card.suit == self.oneSuit:
                return "PENG"
            else:
                return "NOTHING"
        else:
            return "NOTHING"
    
############################################################################################################

class CheatingPlayer(SimpleAIPlayer):
    def __init__(self, id):
        super().__init__(id)
        self.id = f"Cheating_{id}"

    ### Cheat functions
    def _remainingInHand(self, other_player, cardstr):
        return cardsToStr(other_player.hidden).count(cardstr)
    
    def _remainingInDeck(self, cardstr):
        return cardsToStr(self.game.deck).count(cardstr)

    def _dianPao(self, cardstr, afterGang=False):
        losePoint = 0
        gangMult = 2 if afterGang else 1
        for p in self.game.players:
            if p == self:
                continue
            for ting in p.tingList:
                if ting[0] == cardstr:
                    losePoint += ting[1] * gangMult
        return losePoint
    ### End Cheat functions

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
                fake_hidden = self.hidden[0:i]
            else:
                fake_hidden = self.hidden[0:i] + self.hidden[i+1:]
            revealed_tuple, hidden_tuple = self.hashHand()
            tinglist = tingpai( revealed_tuple, tuple(fake_hidden))
            tingscore = 0
            for ting in tinglist:
                tingscore += ting[1] * (sum([self._remainingInHand(p, ting[0]) for p in self.game.players if (p != self and not p.hule)]) + self._remainingInDeck(ting[0])*(0.75+0.25*6)) + 0.001 #别人手里1倍，牌堆25%自摸翻倍收三家
            tingscore_list.append(tingscore)
        
        if len(tingscore_list) > 0 and max(tingscore_list) > 0 and (len(self.game.deck) < 16 or self._dianPao(str(self.hidden[i])) < tingscore * 0.8): #听牌分数超过自己点炮分数的80%
            discard_index = tingscore_list.index(max(tingscore_list))
        else:
            _suit_nums = {'W':[], 'S':[], 'P':[]}
            for card in self.hidden:
                _suit_nums[card.suit].append(card.num)
            _suit_nums_diff_map = {'W':[], 'S':[], 'P':[]}
            for suit in ALL_SUITS:
                if suit == self.shortSuit or len(_suit_nums[suit]) == 0:
                    continue
                _suit_nums_diff_map[suit] = list(np.abs(_suit_nums[suit] - np.mean(_suit_nums[suit])))
            _suit_nums_diff_list = _suit_nums_diff_map['P'] + _suit_nums_diff_map['S'] + _suit_nums_diff_map['W'] # sequence of this should be corresponding to self.hidden

            cardCount = [self.hidden.count(card) for card in self.hidden]
            discardRange = [i for i in range(len(self.hidden)) if cardCount[i] < 2]

            #不点大炮
            for i in discardRange:
                losePoint = self._dianPao(self.hidden[i].__str__())
                if losePoint >= 8 :
                    discardRange.remove(i)

            diff_discard = [_suit_nums_diff_list[i] for i in discardRange]
            if len(discardRange) == 0:
                return self.hidden.pop(np.random.choice(range(len(self.hidden))))
            maxdiff = max(diff_discard)
            discard_index = discardRange[diff_discard.index(maxdiff)]
        return self.hidden.pop(discard_index)

################################################################################################

class ModelBasedPlayer(Player):
    def __init__(self, id, model):
        super().__init__(id)
        self.id = f"ModelBased_{id}"
        self.model = model

    def passThreeCards(self):
        toPass = self.passModel.action(self.hashHand())
        return toPass
    
    def claimShortSuit(self):
        shortSuit = self.shortSuitModel.action(self.hashHand())
        return shortSuit
    
    def anyActionSelf(self):
        actionSelf = self.selfActionModel.action(self.hashHand())
        return actionSelf
    
    def anyActionOther(self, card):
        actionOther = self.otherActionModel.action(self.hashHand(), card)
        return actionOther
    
    def discard(self):
        discard = self.discardModel.action(self.hashHand())
        return discard

################################################################################################

class RandomAIPlayer(SimpleAIPlayer):
    def __init__(self, id, randomLambda=0.1):
        super().__init__(id)
        self.id = f"RandomAI_{id}_{randomLambda}"
        self.randomLambda = randomLambda

    def passThreeCards(self):
        if np.random.random() < self.randomLambda:
            while True:
                toPass = np.random.choice(self.hidden, 3, replace=False)
                if (toPass[0].suit == toPass[1].suit) and (toPass[1].suit == toPass[2].suit):
                    break
            toPass = [self.discardCard(toPass[0]),self.discardCard(toPass[1]),self.discardCard(toPass[2])]
        else:
            toPass = super().passThreeCards()
        return toPass
    
    def claimShortSuit(self):
        if np.random.random() < self.randomLambda:
            shortSuit = np.random.choice(ALL_SUITS)
            self.shortSuit = shortSuit
        else:
            shortSuit = super().claimShortSuit()
        return shortSuit
    
    def anyActionSelf(self):
        if np.random.random() < self.randomLambda:
            legal_actions = ["NOTHING"]
            if self.hu() > 0:
                legal_actions.append("HU")
            if any( [self.canGang(tile, fromHand=True) for tile in self.hidden] ):
                legal_actions.append("GANG")
            actionSelf = np.random.choice(legal_actions)
        else:
            actionSelf = super().anyActionSelf()
        return actionSelf
    
    def anyActionOther(self, card, source_player):
        if np.random.random() < self.randomLambda:
            legal_actions = ["NOTHING"]
            if self.hu() > 0:
                legal_actions.append("HU")
            if self.canGang(card, fromHand=False):
                legal_actions.append("GANG")
            if self.canPeng(card):
                legal_actions.append("PENG")
            actionOther = np.random.choice(legal_actions)
        else:
            actionOther = super().anyActionOther(card, source_player)
        return actionOther
    
    def discard(self):
        if np.random.random() < self.randomLambda:
            discard_index = np.random.randint(0,len(self.hidden))
            discard = self.hidden.pop(discard_index)
        else:
            discard = super().discard()
        return discard