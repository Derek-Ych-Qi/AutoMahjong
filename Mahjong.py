import numpy as np
from itertools import product
from functools import total_ordering
from functools import lru_cache
TOTAL_CARDS = 3 * 9 * 4 #108
ALL_SUITS = ['W', 'S', 'P'] #万条筒
DECK = list( product(ALL_SUITS, range(1,10)) )*4
assert (len(DECK) == TOTAL_CARDS)
MAX_FAN = 7

@total_ordering
class Mahjong(object):
    def __init__(self, id):
        if type(id) == int:
            self.id = id
        elif type(id) == str:
            self.id = int(id[0])-1 + ALL_SUITS.index(id[1]) * 9
        else:
            raise TypeError(f"invalid type {type(id)}")
        self.suit, self.num = DECK[self.id]
        self.unicode_str = ''

    def __str__(self):
        return f"{self.num}{self.suit}"
    
    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.id % 27

    def __eq__(self, other):
        return (self.suit == other.suit) & (self.num == other.num)

    def __lt__(self, other):
        if self.suit == other.suit:
            return self.num < other.num
        else:
            return self.suit < other.suit

    def getUnicode(self):
        #https://en.wikipedia.org/wiki/Mahjong_Tiles_(Unicode_block)
        return chr(0x1F007 + self.__hash__())

@lru_cache
def _isPair(x:tuple) -> bool:
    if len(x) != 2:
        return False
    else:
        return x[0] == x[1]

@lru_cache
def _isKeorGang(x:tuple) -> bool:
    if len(x) < 3:
        return False
    else:
        return all([i == x[0] for i in x])

@lru_cache
def _isSet(x:tuple) -> bool:
    if len(x) != 3:
        return False
    elif x[0].suit != x[1].suit or x[0].suit != x[2].suit or x[2].num - x[0].num >= 3:
        return False
    else:
        if x[0] == x[1] and x[0] == x[2]:
            return True
        elif (x[1].num - x[0].num == 1) & (x[2].num - x[1].num == 1) & (x[0].suit == x[1].suit) & (x[0].suit == x[2].suit):
            return True
        else:
            return False

cardsToStr = lambda cards : [str(c) for c in cards]

@lru_cache
def allPairs(revealed:tuple, hidden:tuple) -> tuple:
    #utilize the sorted feature
    if _isPair(hidden):
        res = list(revealed)
        res.append(hidden)
        return (True, res)
    elif _isPair(hidden[0:2]):
        new_revealed, new_hidden = list(revealed), list(hidden)
        new_revealed.append( (new_hidden.pop(1), new_hidden.pop(0)) )
        #print(tuple(new_revealed), tuple(new_hidden))
        return allPairs(tuple(new_revealed), tuple(new_hidden))
    else:
        return False, []

@lru_cache
def huHelper(revealed:tuple, hidden:tuple) -> tuple:
    #print(revealed, hidden)
    if _isPair(hidden):
        res = list(revealed)
        res.append(hidden)
        return (True, res)
    elif len(hidden) < 2:
        return (False, [])
    else:
        #FIXME this is the source of slowness
        for i in range(0, len(hidden)-2):
            for j in range(i+1, min(i+7, len(hidden)-1)):
                for k in range(j+1, min(i+8, len(hidden))):
                    if _isSet((hidden[i], hidden[j], hidden[k])):
                        new_revealed, new_hidden = list(revealed), list(hidden)
                        new_revealed.append((new_hidden.pop(k), new_hidden.pop(j), new_hidden.pop(i)))
                        hu, style = huHelper(tuple(new_revealed), tuple(new_hidden))
                        if hu:
                            return hu, style
        return False, []

@lru_cache
def hulema(revealed:tuple, hidden:tuple) -> tuple:
    hu, style = False, []
    if len(revealed) == 0:
        hu, style = allPairs(revealed, hidden)
        if hu:
            return hu, style
    hu, style =  huHelper(revealed, hidden)
    return hu, style

@lru_cache
def styleScore(revealed:tuple, hidden:tuple) -> int:
    hu, style = hulema(revealed, hidden)
    if not hu:
        return 0
    fan = 0
    hand = [card for ke in revealed for card in ke] + list(hidden)
    if len(hidden) == 2: #金钩钓
        fan += 1
    if all([_isKeorGang(ke) for ke in style if len(ke) > 2]): #碰碰胡
        fan += 1
    if (min([x.num for x in hand]) > 1) and (max([x.num for x in hand]) < 9): #断幺九
        fan += 1

    if set([x.num for x in hand]).issubset( {2,5,8} ): #258
        fan += 1
    if len(revealed) == 0: #门清
        fan += 1
    if len(set([x.suit for x in hand])) == 1: #清一色
        fan += 2
    if len(style) > 5: #七对
        fan += 1
    card_num = {x: hand.count(x) for x in set(hand)}
    for num in card_num.values():
        if num == 4:
            fan += 1 #根或杠
    return 2 ** fan

def calcScore(revealed:tuple, hidden:tuple, zimo_fan:int) -> int:
    style_score = styleScore(revealed, hidden)
    #点炮=0, 自摸=1, 杠开/海底捞月=2, 杠开且海底捞月=3
    return 2 ** zimo_fan * style_score

@lru_cache
def tingpai(revealed:tuple, hidden:tuple) -> list:
    if len(hidden) == 1:
        return [[hidden[0].__str__(), calcScore(revealed, (hidden[0], hidden[0]), 0)]]
    else:
        tinglist = []
        for i in range(27):
            newcard = Mahjong(id=i)
            if not newcard.suit in [x.suit for x in hidden]:
                continue
            new_hidden = tuple( sorted(list(hidden) + [newcard]) )
            score = calcScore(revealed, new_hidden, 0)
            if score > 0:
                tinglist.append([newcard.__str__(), score])
        return tinglist

def testHu():
    #card_id = np.random.randint(0,TOTAL_CARDS,14)
    #card_id = [0,1,2,3,4,5,6,7,8,27,54,35,62,83] #九莲宝灯
    #card_id = [0,1,2,3,4,5,6,27,28,29,30,31,32,33] #清七对
    #card_id = [0,1,2,3,4,5,27,28,29,30,31,32,59,86] #清龙七对
    #card_id = np.random.randint(0,36,14)
    #card_id = [(x // 9) * 27 + x % 9 for x in card_id]
    #hand = sorted([Mahjong(i) for i in card_id])
    #print(hand)
    revealed = ((Mahjong('9S'),Mahjong('9S'),Mahjong('9S')), (Mahjong('8S'),Mahjong('8S'),Mahjong('8S'),Mahjong('8S')))
    hidden = (Mahjong('2S'),Mahjong('3S'),Mahjong('3S'),Mahjong('4S'),Mahjong('4S'),Mahjong('5S'),Mahjong('6S'),Mahjong('6S'))
    print(calcScore(revealed, hidden, 0))

def testTing():
    revealed = ((Mahjong('9S'),Mahjong('9S'),Mahjong('9S')), (Mahjong('8S'),Mahjong('8S'),Mahjong('8S'),Mahjong('8S')))
    hidden = (Mahjong('2S'),Mahjong('3S'),Mahjong('4S'),Mahjong('4S'),Mahjong('5S'),Mahjong('6S'),Mahjong('6S'))
    print(tingpai(revealed, hidden))

if __name__ == "__main__":
    testHu()
    testTing()