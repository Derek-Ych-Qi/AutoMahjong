import logging
import datetime
import os
import pdb
import numpy as np
import pandas as pd

from Mahjong import *
from Player import *

class Game(object):
    def __init__(self, players, verbose=False, observer=None):
        self.players = players
        for direction, player in zip(['E', 'S', 'W', 'N'], players):
            player.game = self
            player.direction = direction
        self.game_id = f"{datetime.datetime.now()}_{'_'.join([player.id for player in self.players])}"
        self.curr_player = np.random.choice(players)
        self.deck = [Mahjong(i) for i in range(TOTAL_CARDS)]
        np.random.shuffle(self.deck)
        self.gangEvent = []
        self.huEvent = []
        self.logger = logging.getLogger(self.game_id)
        self.logger.info(f"Game {self.game_id} init completed, first player is {self.curr_player.id}")
        self.verbose = verbose
        self.observer = observer

    def getNextPlayer(self, player):
        i = self.players.index(player)
        return self.players[(i+1)%4]

    def getPlayerLists(self):
        return self.players

    def processEvent(self, event):
        if event['source'] == 'all':
            for p in self.players:
                if p == event['player']:
                    p.score += event['score'] * 3
                    self.logger.info(f"Player {p.id} score {event['score']*3}, current score {p.score}")
                else:
                    p.score -= event['score']
                    self.logger.info(f"Player {p.id} score {-1*event['score']}, current score {p.score}")
        else:
            event['player'].score += event['score']
            event['source'].score -= event['score']
            self.logger.info(f"Player {event['player'].id} score {event['score']}, current score {event['player'].score}")
            self.logger.info(f"Player {event['source'].id} score {-1*event['score']}, current score {event['source'].score}")

    def onCardServed(self, card, player, afterGang=False):
        self.logger.info(f"Player {player.id} draw card {card} afterGang={afterGang} remaining deck={len(self.deck)}")
        gameEvent = {'type':'draw', 'player':player, 'card':card, 'afterGang':afterGang}
        if self.observer:
            self.observer.processEvent(gameEvent)
        player.draw(card)
        player_action = player.anyActionSelf()
        if player_action == 'HU':
            #self-draw
            zimo_fan = 1
            if len(self.deck) == 0: #海底捞月
                zimo_fan += 1
            if afterGang: #杠上开花
                zimo_fan += 1

            if card is None or len(player.discardedList) == 0:
                # 天地胡
                score = 2 ** MAX_FAN
            else:
                score = calcScore( *player.hashHand(), zimo_fan)
            gameEvent = {'type':'hu', 'player':player, 'card':card, 'source':'all', 'score':score}
            self.huEvent.append(gameEvent)
            self.logger.info(f"Player {player.id} HU card {card} self draw")
            self.processEvent(self.huEvent[-1])
            if self.observer:
                self.observer.processEvent(gameEvent)
            player.hule = True
            if card:
                player.hidden.remove(card)
            player.huList.append(card)
        elif player_action == 'GANG' and player.canGang(card, fromHand=True) and len(self.deck) > 0: #FIXME 胡了可以杠但是不可改变听的牌
            base = player.gang(card, fromHand=True) #FIXME 杠手中其他牌
            self.logger.info(f"Player {player.id} GANG card {card} self draw")
            gameEvent = {'type':'gang', 'player':player, 'card':card, 'source':'all', 'score':base}
            self.gangEvent.append(gameEvent)
            if self.observer:
                self.observer.processEvent(gameEvent)
            self.processEvent(self.gangEvent[-1])
            self.onCardServed(self.deck.pop(), player, afterGang=True)
        else: #Nothing
            if player.hule:
                self.onCardPlayed(player.discardCard(card), player, afterGang)
            else:
                self.onCardPlayed(player.discard(), player, afterGang)

    def onCardPlayed(self, card, source_player, afterGang=False):
        source_player.discardedList.append(card)
        self.logger.info(f"Player {source_player.id} played card {card} afterGang={afterGang}")
        gameEvent = {'type':'play', 'player':source_player, 'card':card, 'afterGang':afterGang}            
        if self.observer:
                self.observer.processEvent(gameEvent)
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
                gameEvent = {'type':'hu', 'player':player, 'card':card, 'source':source_player, 'score':score}
                self.huEvent.append(gameEvent)
                if self.observer:
                    self.observer.processEvent(gameEvent)
                self.processEvent(self.huEvent[-1])
                player.hule = True
                player.huList.append(card)
                self.curr_player = player
                break
            elif action == "PENG" and player.canPeng(card) and not player.hule:
                self.logger.info(f"Player {player.id} PENG card {card} from player {source_player.id}")
                gameEvent = {'type':'peng', 'player':player, 'card':card, 'source':source_player}
                if self.observer:
                    self.observer.processEvent(gameEvent)
                player.peng(card)
                self.curr_player = player
                self.onCardPlayed(player.discard(), player, False)
                break
            elif action == "GANG" and player.canGang(card, fromHand=False) and len(self.deck) > 0:
                self.logger.info(f"Player {player.id} GANG card {card} from player {source_player.id}")
                base = player.gang(card, fromHand=False)
                gameEvent = {'type':'gang', 'player':player, 'card':card, 'source':source_player, 'score':base}
                self.gangEvent.append(gameEvent)
                if self.observer:
                    self.observer.processEvent(gameEvent)
                self.processEvent(self.gangEvent[-1])
                self.curr_player = player
                self.onCardServed(self.deck.pop(), player, afterGang=True)
                break
            else:
                continue
    
    def start(self):
        #initial hand
        player = self.curr_player
        for i in range(52):
            card = self.deck.pop(0)
            player.draw(card)
            if self.observer:
                self.observer.processEvent({'type':'draw', 'player':player, 'card':card, 'afterGang':False})
            player = self.getNextPlayer(player)
        card= self.deck.pop(0)
        self.curr_player.draw(card)
        if self.observer:
            self.observer.processEvent({'type':'draw', 'player':player, 'card':card, 'afterGang':False})
        #pass three cards
        passing_index = np.random.randint(1,3)
        passing_cards = {}
        for player in self.players:
            passing_cards[player] = player.passThreeCards()
        for player in self.players:
            dest_index = (self.players.index(player) + passing_index) % 4 # 1: next player, 2: player across, 3: previous player
            dest_player = self.players[dest_index]
            dest_player.draw(passing_cards[player])
            if self.observer:
                for card in passing_cards[player]:
                    self.observer.processEvent({'type':'pass', 'player':dest_player, 'card':card, 'source':player})

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
        if self.verbose:
            self.summary()
        if self.observer:
            self.observer.end()
    
    def end(self):
        self.logger.info("### End Game ###")
        self.logger.info("Check Ting")
        for player in self.players:
            player.ting()
            suits = set([card.suit for card in player.hidden])
            if len(suits) == 3:
                self.logger.info(f"Player {player.id} has short suit remaining by end game")
                eventHuaZhu = {'type':'huazhu', 'player':player, 'source':'all', 'score':-2**MAX_FAN}
                self.processEvent(eventHuaZhu)
                if self.observer:
                    self.observer.processEvent(eventHuaZhu)
        players_meihu = [p for p in self.players if not p.hule]
        players_tingle = [p for p in players_meihu if len(p.tingList) > 0]
        players_meiting = [p for p in players_meihu if len(p.tingList) == 0]
        for p_t in players_tingle:
            score = max([score for (card, score) in p_t.tingList])
            for p_mt in players_meiting:
                eventDaJiao = {'type':'dajiao', 'player':p_t, 'source':p_mt, 'score':score}
                self.processEvent(eventDaJiao)
                if self.observer:
                    self.observer.processEvent(eventDaJiao)
        self.logger.info("Gang Tax Refund")
        for ge in self.gangEvent:
            base = ge['score']
            if ge['player'] in players_meiting:
                reverse_ge = {'type':'rev_gang', 'player':ge['player'], 'source':ge['source'], 'score':-1*ge['score']}
                self.processEvent(reverse_ge)
                if self.observer:
                    self.observer.processEvent(reverse_ge)

    def summary(self):
        for huEvent in self.huEvent:
            p, s = huEvent['player'], huEvent['source']
            print(f"player:{p.id}, source:{s if type(s) == str else s.id}, score:{huEvent['score']}")
        for player in self.players:
            player.currentState()

    def getPublicInfo(self):
        info = {}
        info['remaining_deck'] = len(self.deck)
        for p in self.players:
            pInfo = p.getPublicInfo()
            info.update({p.id : pInfo})
        return info
    
    def displayPublicInfo(self):
        info = self.getPublicInfo()
        print(f"remaining deck: {info['remaining_deck']}")
        for p in self.players:
            p.displayPublicInfo()

class Observer(object):
    def __init__(self):
        self.current_event_id = 0
        self.all_events = []
        self.logDir = './gamelog'
        self.id = datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
    
    def processEvent(self, event):
        self.current_event_id += 1
        event.update({'id':self.current_event_id})
        self.all_events.append(event)
    
    def end(self):
        for event in self.all_events:
            if isinstance(event.get('player'), Player):
                event['player'] = event['player'].direction
            if isinstance(event.get('source'), Player):
                event['source'] = event['source'].direction
        event_df = pd.DataFrame(self.all_events)
        event_df.to_csv(os.path.join(self.logDir, f'event_{self.id}.csv'), index=False)

class GameLogReader(object):
    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)
        self.players = [Player('E'), Player('S'), Player('W'), Player('N')]
        self.playersMap = dict(zip(['E', 'S', 'W', 'N'], self.players))
    
    def processLogEvent(self, event):
        if event['type'] == 'draw':
            if not pd.isnull(event['card']):
                self.playersMap.get(event['player']).draw( Mahjong(event['card']) )
        elif event['type'] == 'play':
            self.playersMap.get(event['player']).discardCardStr(event['card'])
        elif event['type'] == 'pass':
            self.playersMap.get(event['source']).discardCardStr(event['card'])
            self.playersMap.get(event['player']).draw( Mahjong(event['card']) )
        elif event['type'] == 'peng':
            self.playersMap.get(event['player']).peng(Mahjong(event['card']))
        elif event['type'] == 'gang':
            self.playersMap.get(event['player']).gang(Mahjong(event['card']))
            if event['source'] == 'all':
                for p in self.players:
                    if p != self.playersMap.get(event['player']):
                        p.score -= event['score']
                    else:
                        p.score += event['score'] * 3
            else:
                self.playersMap.get(event['source']).score -= event['score']
                self.playersMap.get(event['player']).score += event['score']
        elif event['type'] == 'hu':
            self.playersMap.get(event['player']).hule = True
            if event['source'] == 'all':
                for p in self.players:
                    if p != self.playersMap.get(event['player']):
                        p.score -= event['score']
                    else:
                        p.score += event['score'] * 3
                self.playersMap.get(event['player']).discardCardStr(event['card'])
                self.playersMap.get(event['player']).huList.append(Mahjong(event['card']))
            else:
                self.playersMap.get(event['source']).score -= event['score']
                self.playersMap.get(event['player']).score += event['score']
                self.playersMap.get(event['player']).huList.append(Mahjong(event['card']))
        elif event['type'] == 'huazhu' or event['type'] == 'dajiao' or event['type'] == 'rev_gang':
            if event['source'] == 'all':
                for p in self.players:
                    if p != self.playersMap.get(event['player']):
                        p.score -= event['score']
                    else:
                        p.score += event['score'] * 3
            else:
                self.playersMap.get(event['source']).score -= event['score']
                self.playersMap.get(event['player']).score += event['score']
    
    def run(self):
        for i, row in self.data.iterrows():
            self.processLogEvent(row)

        for player in self.players:
            player.currentState()


    