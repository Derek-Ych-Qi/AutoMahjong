import logging
import datetime
import itertools
import pdb
import numpy as np

from Mahjong import *
from Player import *

class Game(object):
    def __init__(self, players):
        self.players = players
        for player in players:
            player.game = self
        self.game_id = f"{datetime.datetime.now()}_{'_'.join([player.id for player in self.players])}"
        self.curr_player = np.random.choice(players)
        self.deck = [Mahjong(i) for i in range(TOTAL_CARDS)]
        np.random.shuffle(self.deck)
        self.gangEvent = []
        self.logger = logging.getLogger(self.game_id)
        self.logger.info(f"Game {self.game_id} init completed, first player is {self.curr_player.id}")

    def getNextPlayer(self, player):
        i = self.players.index(player)
        return self.players[(i+1)%4]

    def getPlayerLists(self):
        return self.players

    def onCardServed(self, card, player, afterGang=False):
        self.logger.info(f"Player {player.id} draw card {card} afterGang={afterGang} remaining deck={len(self.deck)}")
        player.draw(card)
        player_action = player.anyActionSelf()
        if player_action == 'HU':
            #self-draw
            zimo_fan = 1
            if len(self.deck) == 0: #海底捞月
                zimo_fan += 1
            if afterGang: #杠上开花
                zimo_fan += 1

            score = calcScore( *player.hashHand(), zimo_fan)
            self.logger.info(f"Player {player.id} HU card {card} self draw")
            for p in self.players:
                if p == player:
                    p.score += score * 3
                    self.logger.info(f"Player {p.id} score +{score*3}, current score {p.score}")
                else:
                    p.score -= score
                    self.logger.info(f"Player {p.id} score -{score}, current score {p.score}")
            player.hidden.remove(card)
            player.hule = True
            player.huList.append(card)
        elif player_action == 'GANG' and player.canGang(card, fromHand=True):
            base = player.gang(card, fromHand=True) #FIXME 杠手中其他牌
            self.logger.info(f"Player {player.id} GANG card {card} self draw")
            self.gangEvent.append({'cr':player, 'de':'all', 'base':base})
            for p in self.players:
                if p == player:
                    p.score += base * 3
                    self.logger.info(f"Player {p.id} score +{3*base}, current score {p.score}")
                else:
                    p.score -= base
                    self.logger.info(f"Player {p.id} score -{base}, current score {p.score}")
            self.onCardServed(self.deck.pop(), player, afterGang=True)
        else: #Nothing
            if player.hule:
                self.onCardPlayed(player.discardCard(card), player, afterGang)
            else:
                self.onCardPlayed(player.discard(), player, afterGang)

    def onCardPlayed(self, card, source_player, afterGang=False):
        self.logger.info(f"Player {source_player.id} played card {card} afterGang={afterGang}")
        action_list_others = []
        for player in self.players:
            if player == source_player:
                continue
            player_action = player.anyActionOther(card, source_player)
            action_list_others.append((player, player_action))
        # hu > peng/gang
        for player, action in action_list_others:
            if action == "HU":
                gangFan = 1 if afterGang else 0
                for player1, action1 in action_list_others:
                    if action1 == "GANG":
                        #抢杠胡
                        source_player = player1
                        gangFan += 1
                score = calcScore( player.hashHand()[0], tuple(sorted(player.hidden+[card])), gangFan)
                player.score += score
                source_player.score -= score
                self.logger.info(f"Player {player.id} score +{score}, current score {player.score}")
                self.logger.info(f"Player {source_player.id} score -{score}, current score {source_player.score}")
                player.hule = True
                player.huList.append(card)
                self.curr_player = player
                break
            elif action == "PENG" and player.canPeng(card) and not player.hule:
                self.logger.info(f"Player {player.id} PENG card {card} from player {source_player.id}")
                player.peng(card)
                self.curr_player = player
                self.onCardPlayed(player.discard(), player, False)
                break
            elif action == "GANG" and player.canGang(card, fromHand=False):
                self.logger.info(f"Player {player.id} GANG card {card} from player {source_player.id}")
                base = player.gang(card, fromHand=False)
                player.score += base
                source_player.score -= base
                self.logger.info(f"Player {player.id} score +{base}, current score {player.score}")
                self.logger.info(f"Player {source_player.id} score -{base}, current score {source_player.score}")
                self.gangEvent.append({'cr':player, 'de':source_player, 'base':base})
                self.curr_player = player
                self.onCardServed(self.deck.pop(), player, afterGang=True)
                break
            else:
                continue
    
    def start(self):
        #initial hand
        player = self.curr_player
        for i in range(52):
            player.draw(self.deck.pop(0))
            player = self.getNextPlayer(player)
        self.curr_player.draw(self.deck.pop(0))
        #pass three cards
        passing_index = np.random.randint(1,3)
        passing_cards = {}
        for player in self.players:
            passing_cards[player] = player.passThreeCards()
        for player in self.players:
            dest_index = (self.players.index(player) + passing_index) % 4 # 1: next player, 2: player across, 3: previous player
            dest_player = self.players[dest_index]
            dest_player.draw(passing_cards[player])

        #claim short suit
        for p in self.players:
            p.claimShortSuit()
        #regular game
        self.onCardServed(None, self.curr_player, False) # Dealer play first card
        while len(self.deck) > 0:
            self.curr_player = self.getNextPlayer(self.curr_player)
            self.onCardServed(self.deck.pop(0), self.curr_player, afterGang=False)
        #end game
        self.end()
        self.summary()
    
    def end(self):
        self.logger.info("### End Game ###")
        self.logger.info("Check Ting")
        for player in self.players:
            player.ting()
            suits = set([card.suit for card in player.hidden])
            if len(suits) == 3:
                self.logger.info(f"Player {player.id} has short suit remaining by end game")
                for p in self.players:
                    if p == player:
                        p.score -= 2 ** MAX_FAN * 3
                        self.logger.info(f"Player {player.id} score -{2 ** MAX_FAN * 3}, current score {player.score}")
                    else:
                        p.score += 2 ** MAX_FAN
                        self.logger.info(f"Player {player.id} score +{2 ** MAX_FAN}, current score {player.score}")
        players_meihu = [p for p in self.players if not p.hule]
        players_tingle = [p for p in players_meihu if len(p.tingList) > 0]
        players_meiting = [p for p in players_meihu if len(p.tingList) == 0]
        for p_t in players_tingle:
            score = max([score for (card, score) in p_t.tingList])
            for p_mt in players_meiting:
                p_mt.score -= score
                p_t.score += score
                self.logger.info(f"Player {p_mt.id} score -{score}, current score {p_mt.score}")
                self.logger.info(f"Player {p_t.id} score +{score}, current score {p_t.score}")
        self.logger.info("Gang Tax Refund")
        for ge in self.gangEvent:
            base = ge['base']
            if ge['cr'] in players_meiting:
                if ge['de'] == 'all':
                    for p in self.players:
                        if p == ge['cr']:
                            p.score -= base*3
                            self.logger.info(f"Player {p.id} score -{3*base}, current score {p.score}")
                        else:
                            p.score += base
                            self.logger.info(f"Player {p.id} score +{base}, current score {p.score}")
                else:
                    ge['cr'].score -= base
                    ge['de'].score += base
                    self.logger.info(f"Player {ge['cr'].id} score -{base}, current score {ge['cr'].score}")
                    self.logger.info(f"Player {ge['de'].id} score -{base}, current score {ge['de'].score}")

        
    def summary(self):
        for player in self.players:
            player.currentState()
