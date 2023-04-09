import numpy as np
from itertools import product
from functools import total_ordering
TOTAL_CARDS = 3 * 9 * 4 #108
ALL_SUITS = ['W', 'S', 'P'] #万条筒
DECK = list( product(ALL_SUITS, range(1,10)) )*4
assert (len(DECK) == TOTAL_CARDS)
MAX_FAN = 7

@total_ordering
class Mahjong(object):
    def __init__(self, id):
        self.id = id
        self.suit, self.num = DECK[id]
        self.unicode_str = ''

    def __str__(self):
        return f"{self.num}{self.suit}"
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.suit == other.suit) & (self.num == other.num)

    def __lt__(self, other):
        if self.suit == other.suit:
            return self.num < other.num
        else:
            return self.suit < other.suit

    @staticmethod
    def getUnicode(card_str):
        #https://en.wikipedia.org/wiki/Mahjong_Tiles_(Unicode_block)
        pass

def _isPair(x:list) -> bool:
    if len(x) != 2:
        return False
    else:
        return x[0] == x[1]

def _isKeorGang(x:list) -> bool:
    if len(x) < 3:
        return False
    else:
        return all([i == x[0] for i in x])

def _isSet(x:list) -> bool:
    if len(x) != 3:
        return False
    else:
        if x[0] == x[1] and x[0] == x[2]:
            return True
        elif (x[1].num - x[0].num == 1) & (x[2].num - x[1].num == 1) & (x[0].suit == x[1].suit) & (x[0].suit == x[2].suit):
            return True
        else:
            return False

def allPairs(revealed, hidden):
    #utilize the sorted feature
    if _isPair(hidden):
        revealed.append(hidden)
        return (True, revealed)
    elif _isPair(hidden[0:2]):
        new_revealed, new_hidden = revealed.copy(), hidden.copy()
        new_revealed.append([new_hidden.pop(1), new_hidden.pop(0)])
        return allPairs(new_revealed, new_hidden)
    else:
        return (False, [])


def huHelper(revealed, hidden):
    #print(revealed, hidden)
    if _isPair(hidden):
        new_revealed = revealed.copy()
        new_revealed.append(hidden)
        return (True, new_revealed)
    elif len(hidden) < 2:
        return (False, [])
    else:
        for i in range(0, len(hidden)-2):
            for j in range(i+1, len(hidden)-1):
                for k in range(j+1, len(hidden)):
                    if _isSet([hidden[i], hidden[j], hidden[k]]):
                        new_revealed, new_hidden = revealed.copy(), hidden.copy()
                        new_revealed.append([new_hidden.pop(k), new_hidden.pop(j), new_hidden.pop(i)])
                        hu, style = huHelper(new_revealed, new_hidden)
                        if hu:
                            return hu, style
        return (False, [])

def hulema(revealed, hidden):
    hu, style = False, []
    if len(revealed) == 0:
        hu, style = allPairs(revealed, hidden)
        if hu:
            return hu, style
    hu, style =  huHelper(revealed, hidden)
    return hu, style


def calcScore(revealed, hidden, zimo_fan):
    hu, style = hulema(revealed, hidden)
    if not hu:
        return 0
    fan = zimo_fan #点炮=0, 自摸=1, 杠开/海底捞月=2, 杠开且海底捞月=3
    hand = [card for ket in revealed for card in ket] + hidden
    if len(hidden) == 2: #金钩钓
        fan += 1
    if all([_isKeorGang(ket) for ket in style if len(ket) > 2]): #碰碰胡
        fan += 1
    if (min([x.num for x in hand]) > 1) and (max([x.num for x in hand]) < 9): #断幺九
        fan += 1

    if set([x.num for x in hand]).issubset( {2,5,8} ): #258
        fan += 1
    if len(revealed) == 0: #门清
        fan += 1
    if len(set([x.suit for x in hand])) == 1: #清一色
        fan += 1
    if len(style) > 5: #七对
        fan += 1
    for ket in style: #杠
        if len(ket) == 4:
            fan += 1

    return 2 ** fan

def tingpai(revealed, hidden):
    if len(hidden) == 1:
        return [[hidden[0].__str__(), calcScore(revealed, hidden*2, 0)]]
    else:
        tinglist = []
        for i in range(27):
            newcard = Mahjong(id=i)
            if not newcard.suit in [x.suit for x in hidden]:
                continue
            score = calcScore(revealed, hidden + [newcard], 0)
            if score > 0:
                tinglist.append([newcard.__str__(), score])
        return tinglist

def testHu():
    #card_id = np.random.randint(0,TOTAL_CARDS,14)
    card_id = [0,1,2,3,4,5,6,7,8,27,54,35,62,83] #九莲宝灯
    #card_id = [0,1,2,3,4,5,6,27,28,29,30,31,32,33] #清七对
    #card_id = [0,1,2,3,4,5,27,28,29,30,31,32,59,86] #清龙七对
    #card_id = np.random.randint(0,36,14)
    #card_id = [(x // 9) * 27 + x % 9 for x in card_id]
    hand = sorted([Mahjong(i) for i in card_id])
    print(hand)
    print(hulema([], hand), calcScore([], hand))

def testTing():
    card_id = [0,1,2,3,4,5,6,7,8,27,54,35,62]
    hand = sorted([Mahjong(i) for i in card_id])
    print(tingpai([], hand))

if __name__ == "__main__":
    testTing()