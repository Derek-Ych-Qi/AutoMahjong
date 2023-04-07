import logging
import datetime
import itertools
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
        self.logger = logging.getLogger(self.game_id)
        self.logger.info(f"Game {self.game_id} init completed, first player is {self.curr_player.id}")

    def getNextPlayer(self, player):
        i = self.players.index(player)
        return self.players[(i+1)%4]

    def getPrevPlayer(self, player):
        i = self.players.index(player)
        return self.players[i-1]

    def onCardServed(self, card, player, afterGang=False):
        self.logger.info(f"Player {player.id} draw card {card} afterGang={afterGang}")
        player.draw(card)
        player_action = player.anyAction()
        if player_action == 'HU':
            #self-draw
            zimo_fan = 1
            if len(self.deck) == 0:
                zimo_fan += 1
            if afterGang:
                zimo_fan += 1

            score, style = calcScore(player.revealed, player.hidden, zimo_fan)
            self.logger.info(f"Player {player.id} HU card {card} self draw")
            for p in self.players:
                if p == player:
                    p.score += score * 3
                    self.logger.info(f"Player {player.id} score +{score*3}, current score {player.score}")
                else:
                    p.score -= score
                    self.logger.info(f"Player {player.id} score -{score}, current score {player.score}")
            player.hidden.remove(card)
            player.huList.append(card)
        elif player_action == 'GANG':
            self.logger.info(f"Player {player.id} GANG card {card} self draw")
            for p in self.players:
                if p == player:
                    p.score += 2 * 3
                    self.logger.info(f"Player {player.id} score +6, current score {player.score}")
                else:
                    p.score -= 2
                    self.logger.info(f"Player {player.id} score -2, current score {player.score}")
            self.onCardServed(self.deck.pop(), player, afterGang=True)
        else: #Nothing
            self.onCardPlayed(player.discard(), player, afterGang)

    def onCardPlayed(self, card, source_player, afterGang=False):
        self.logger.info(f"Player {source_player} played card {card} afterGang={afterGang}")
        action_list_others = []
        for player in self.players:
            if player == source_player:
                continue
            player_action = player.anyAction(card, source_player)
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
                score, style = calcScore(player.revealed, sorted(player.hidden+[card]), gangFan)
                player.score += score
                source_player.score -= score
                player.huList.append(card)
                self.curr_player = player
                break
            elif action == "PENG":
                player.peng(card)
                self.curr_player = player
                self.onCardPlayed(player.discard(), player, False)
                break
            elif action == "GANG":
                player.gang(card)
                self.curr_player = player
                self.onCardPlayed(player.discard(), player, True)
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
        #pass card

        #claim short suit
        for p in self.players:
            p.claimShortSuit()
        #regular game
        while len(self.deck) > 0:
            self.curr_player = self.getNextPlayer(self.curr_player)
            self.onCardServed(self.deck.pop(0), self.curr_player, afterGang=False)
