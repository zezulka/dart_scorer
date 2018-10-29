import unittest

from dartscorer.tests.test_common import *
from dartscorer.input.input_controller import Event, EventType, Action
from dartscorer.logic.cricket import Cricket, cricket_score_init


class TestCricket(unittest.TestCase):

    def test_game_over(self):
        evs = [
            Event(EventType.NUMBER, 1),
            Event(EventType.NUMBER, 5),
            Event(EventType.ACTION, Action.CONFIRM),
        ]
        game = Cricket(1, TestingPoller(evs * 6), RENDERER)
        self.assertFalse(game.over())
        game.loop()
        self.assertFalse(game.over())

    def test_single_score(self):
        evs = [
            Event(EventType.NUMBER, 1),
            Event(EventType.NUMBER, 5),
            Event(EventType.ACTION, Action.CONFIRM)
        ]
        game = Cricket(1, TestingPoller(evs), RENDERER)
        expected = cricket_score_init()
        self.assertEqual(game.players[0], expected)
        game.loop()
        expected[15] = expected[15] + 1
        self.assertEqual(game.players[0], expected)
