import unittest

from dartscorer.tests.test_common import *
from dartscorer.input.input_controller import Event, EventType, Action
from dartscorer.logic.cricket import Cricket, cricket_score_init


class TestCricket(unittest.TestCase):

    def setUp(self):
        RENDERER.clear()
        print("\n\n--- {} ---".format(self.id()), file=RENDERER.output_file)

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
        str = RENDERER.to_string()
        expected = cricket_score_init()
        self.assertEqual(game.players[0], expected)
        game.loop()
        expected[15] = 1
        self.assertEqual(game.players[0], expected)

    def test_triple_score(self):
        evs = [
            Event(EventType.NUMBER, 1),
            Event(EventType.NUMBER, 5),
            Event(EventType.ACTION, Action.TRIPLE),
            Event(EventType.ACTION, Action.CONFIRM)
        ]
        game = Cricket(1, TestingPoller(evs), RENDERER)
        expected = cricket_score_init()
        game.loop()
        expected[15] = 3
        self.assertEqual(game.players[0], expected)

    def test_score_overflow(self):
        evs = [
            Event(EventType.NUMBER, 1),
            Event(EventType.NUMBER, 5),
            Event(EventType.ACTION, Action.TRIPLE),
            Event(EventType.ACTION, Action.CONFIRM)
        ] * 2
        game = Cricket(1, TestingPoller(evs), RENDERER)
        expected = cricket_score_init()
        game.loop()
        expected[15] = 3
        self.assertEqual(game.players[0], expected)

    def test_score_overflow_second(self):
        evs = [
            Event(EventType.NUMBER, 1),
            Event(EventType.NUMBER, 5),
            Event(EventType.ACTION, Action.DOUBLE),
            Event(EventType.ACTION, Action.CONFIRM)
        ] * 3
        game = Cricket(1, TestingPoller(evs), RENDERER)
        expected = cricket_score_init()
        game.loop()
        expected[15] = 3
        self.assertEqual(game.players[0], expected)

    def test_score_seven_finisher(self):
        evs = []
        for i in range(5,10):
            evs += [
                Event(EventType.NUMBER, 1),
                Event(EventType.NUMBER, i),
                Event(EventType.ACTION, Action.TRIPLE),
                Event(EventType.ACTION, Action.CONFIRM)
            ]
        evs += [
            Event(EventType.NUMBER, 2),
            Event(EventType.NUMBER, 0),
            Event(EventType.ACTION, Action.TRIPLE),
            Event(EventType.ACTION, Action.CONFIRM)
        ]
        evs += [
            Event(EventType.NUMBER, 2),
            Event(EventType.NUMBER, 5),
            Event(EventType.ACTION, Action.CONFIRM)
        ] * 3
        game = Cricket(1, TestingPoller(evs), RENDERER)
        game.loop()
        self.assertTrue(game.over())