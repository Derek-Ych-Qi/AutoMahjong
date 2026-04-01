import unittest
import Game
from Mahjong import calcScore, Mahjong
from Player import Player

class TestGame(unittest.TestCase):
    def setUp(self):
        self.players = [Player("p1"), Player("p2"), Player("p3"), Player("p4")]
        self.game = Game(self.players)

    def test_initialization(self):
        self.assertEqual(len(self.game.deck), 136)
        self.assertIn(self.game.curr_player, self.players)
        self.assertEqual(self.game.logger.name, self.game.game_id)
        for player in self.players:
            self.assertEqual(player.game, self.game)

    def test_getNextPlayer(self):
        self.assertEqual(self.game.getNextPlayer(self.players[0]), self.players[1])
        self.assertEqual(self.game.getNextPlayer(self.players[3]), self.players[0])

    def test_getPrevPlayer(self):
        self.assertEqual(self.game.getPrevPlayer(self.players[0]), self.players[3])
        self.assertEqual(self.game.getPrevPlayer(self.players[3]), self.players[2])

    def test_onCardServed(self):
        card = self.game.deck[-1]
        self.game.onCardServed(card, self.game.curr_player)
        self.assertEqual(len(self.game.deck), 135)
        self.assertNotIn(card, self.game.deck)
        self.assertIn(card, self.game.curr_player.hidden)
        self.assertTrue(self.game.curr_player.hule or self.game.curr_player.anyActionSelf() != "HU")

    def test_onCardPlayed_with_HU(self):
        for player in self.players:
            player.hule = False
        card = self.players[0].hidden[0]
        self.players[0].anyActionOther(card, self.players[1])
        self.game.onCardPlayed(card, self.players[1])
        self.assertTrue(self.players[0].hule)
        self.assertEqual(self.players[0].huList[-1], card)
        self.assertGreater(self.players[0].score, self.players[1].score)
        self.assertEqual(self.game.curr_player, self.players[0])

    def test_onCardPlayed_with_PENG(self):
        card = self.game.curr_player.hidden[0]
        self.game.onCardPlayed(card, self.game.curr_player)
        self.assertNotIn(card, self.game.curr_player.hidden)
        self.assertIn(card, self.game.curr_player.revealed)
        self.assertNotEqual(self.game.curr_player, self.players[0])
        for player in self.players:
            if player != self.game.curr_player:
                self.assertEqual(player.anyActionOther(card, self.game.curr_player), "PENG")


class TestMahjong(unittest.TestCase):
    def test_calcScore(self):
        # Test case 1: all simples
        revealed = [Mahjong(0), Mahjong(1), Mahjong(2), Mahjong(3), Mahjong(4), Mahjong(5), Mahjong(6)]
        hidden = [Mahjong(7), Mahjong(8), Mahjong(9), Mahjong(10), Mahjong(11), Mahjong(12), Mahjong(13)]
        self.assertEqual(calcScore(revealed, hidden, 0), 1)

        # Test case 2: seven pairs
        revealed = []
        hidden = [Mahjong(0), Mahjong(0), Mahjong(1), Mahjong(1), Mahjong(2), Mahjong(2), Mahjong(3), Mahjong(3), Mahjong(4), Mahjong(4), Mahjong(5), Mahjong(5), Mahjong(6), Mahjong(6)]
        self.assertEqual(calcScore(revealed, hidden, 0), 64)

        # Test case 3: all terminals and honors
        revealed = [Mahjong(0), Mahjong(8), Mahjong(9), Mahjong(17), Mahjong(18), Mahjong(26)]
        hidden = [Mahjong(1), Mahjong(2), Mahjong(3), Mahjong(4), Mahjong(5), Mahjong(6), Mahjong(7), Mahjong(10), Mahjong(11), Mahjong(12), Mahjong(13), Mahjong(14), Mahjong(15), Mahjong(16), Mahjong(19), Mahjong(20), Mahjong(21), Mahjong(22), Mahjong(23), Mahjong(24), Mahjong(25)]
        self.assertEqual(calcScore(revealed, hidden, 0), 88)


if __name__ == '__main__':
    unittest.main()