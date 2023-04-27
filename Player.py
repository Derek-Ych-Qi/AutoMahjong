import logging
from Mahjong import *

PLAYER_ACTIONS = ["NOTHING", "HU", "PENG", 'GANG']

class Player(object):
    def __init__(self):
        self.id = None
        self.direction = None
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
        raise NotImplementedError

    def claimShortSuit(self):
        raise NotImplementedError

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
        raise NotImplementedError

    def anyActionOther(self, card:Mahjong, source_player) -> str:
        """
        card is played by other player
        peng, gang or hu or do nothing
        """
        raise NotImplementedError

    def discard(self) -> Mahjong:
        """
        player discard a card, return the played card
        """
        raise NotImplementedError

    def discardCard(self, card:Mahjong) -> Mahjong:
        """
        discard by card instance, return played card
        """
        return self.discardCardStr(str(card))

    def discardCardStr(self, card_str) -> Mahjong:
        """
        discard by card name
        """
        i = cardsToStr(self.hidden).index(card_str)
        return self.hidden.pop(i)
    
    def canPeng(self, card) -> bool:
        hidden_str = cardsToStr(self.hidden)
        return hidden_str.count(str(card)) >= 2

    def peng(self, card) -> bool:
        i = cardsToStr(self.hidden).index(str(card))
        j = cardsToStr(self.hidden).index(str(card), i+1)
        card1 = self.hidden.pop(j)
        card2 = self.hidden.pop(i)
        self.revealed.append([card1, card2, card])
        return True
    
    def canGang(self, card, fromHand=False):
        hidden_str = cardsToStr(self.hidden)
        if fromHand:
            #杠明刻
            for ke in self.revealed:
                if str(ke[0]) == str(card):
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
            for ke in self.revealed:
                if str(ke[0]) == str(card):
                    ke.append(card) #明杠
                    self.hidden.remove(card)
                return 1
            if cardsToStr(self.hidden).count(str(card)) >= 4:
                i = cardsToStr(self.hidden).index(str(card))
                j = cardsToStr(self.hidden).index(str(card), i+1)
                k = cardsToStr(self.hidden).index(str(card), j+1)
                l = cardsToStr(self.hidden).index(str(card), k+1)
                self.revealed.append([self.hidden.pop(l), self.hidden.pop(k), self.hidden.pop(j), self.hidden.pop(i)])
                return 2
        else:
            i = cardsToStr(self.hidden).index(str(card))
            j = cardsToStr(self.hidden).index(str(card), i+1)
            k = cardsToStr(self.hidden).index(str(card), j+1)
            self.revealed.append([self.hidden.pop(k), self.hidden.pop(j), self.hidden.pop(i), card])
            return 1

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
        info['score'] = self.score
        info['revealed'] = self.revealed
        info['played'] = self.discardedList
        info['hule'] = self.hule
        info['huList'] = self.huList
        return info
    
    def displayPublicInfo(self):
        info = self.getPublicInfo()
        infoStr = f"{self.id}, score: {info['score']}, shortSuit: {info['shortSuit']}, revealed: {info['revealed']}, played: {info['played']}"
        if self.hule:
            infoStr += f", huList: {info['huList']}"
        print(infoStr)

